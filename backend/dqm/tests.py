# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import date, datetime
import unittest

from django.test import TestCase
from django.utils import timezone
from dqm import errors
import dqm.check_bricks as cb
from dqm.models import ApiCache, Check, CheckExecution, Status, Suite, SuiteExecution

class TestParameter(TestCase):

  def test_cast_boolean_true(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.BOOLEAN)
    v = p.cast('true')
    self.assertEqual(type(v), bool)
    self.assertEqual(v, True)

  def test_cast_boolean_false(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.BOOLEAN)
    v = p.cast('false')
    self.assertEqual(type(v), bool)
    self.assertEqual(v, False)

  def test_cast_boolean_empty_string(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.BOOLEAN)
    v = p.cast('')
    self.assertEqual(type(v), bool)
    self.assertEqual(v, False)

  def test_cast_boolean_none(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.BOOLEAN)
    v = p.cast(None)
    self.assertEqual(type(v), bool)
    self.assertEqual(v, False)

  def test_cast_string(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.STRING)
    v = p.cast('test string')
    self.assertEqual(type(v), str)
    self.assertEqual(v, 'test string')

  def test_cast_list(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.LIST)
    v = p.cast('1,2,3')
    self.assertEqual(type(v), list)
    self.assertEqual(v, ['1', '2', '3'])

  def test_cast_list_empty(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.LIST)
    v = p.cast('')
    self.assertEqual(type(v), list)
    self.assertEqual(v, [])

  def test_cast_list_none(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.LIST)
    v = p.cast(None)
    self.assertEqual(type(v), list)
    self.assertEqual(v, [])

  def test_validate_empty_str(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.STRING, default='test')
    v = p.validate('')
    self.assertEqual(type(v), str)
    self.assertEqual(v, 'test')

  def test_validate_none(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.STRING, default='test')
    v = p.validate(None)
    self.assertEqual(type(v), str)
    self.assertEqual(v, 'test')

  def test_cast_str_date(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.DATE)
    v = p.cast('2010-01-01')
    self.assertEqual(type(v), date)
    self.assertEqual(v, date(2010, 1, 1))

  def test_cast_empty_str_date(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.DATE)
    v = p.cast('')
    self.assertEqual(type(v), date)

  def test_cast_none_date(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.DATE)
    v = p.cast(None)
    self.assertEqual(type(v), date)

  def test_cast_str_datetime(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.DATETIME, default=None)
    v = p.cast('2010-01-01')
    self.assertEqual(type(v), datetime)
    self.assertEqual(v, datetime(2010, 1, 1))

  def test_cast_empty_str_datetime(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.DATETIME, default=None)
    v = p.cast('')
    self.assertEqual(type(v), datetime)

  def test_cast_none_datetime(self):
    p = cb.Parameter(name='', title='', data_type=cb.DataType.DATETIME, default=None)
    v = p.cast(None)
    self.assertEqual(type(v), datetime)


class TestCheck(TestCase):

  def test_check_declaration(self):
    class MyCheck(cb.Check):
      title = 'My check'
      description = 'A description'
      result_fields = [
        cb.ResultField(name='my_result', data_type=cb.DataType.STRING),
      ]

    metadata = MyCheck.get_metadata()
    self.assertIsInstance(metadata, dict)

  def test_check_declaration_missing_metadata(self):
    class MyCheck(cb.Check):
      title = 'My check'
    # The description field is required.
    with self.assertRaises(errors.MissingMetadata):
      MyCheck.get_metadata()

  def test_check_declaration_with_params(self):
    class MyCheck(cb.Check):
      title = 'My check'
      description = 'A description'
      parameters = [
        cb.Parameter(name='my_param', data_type=cb.DataType.STRING),
        cb.Parameter(name='other_param', data_type=cb.DataType.INT),
      ]
      result_fields = [
        cb.ResultField(name='my_result', data_type=cb.DataType.STRING),
      ]

    metadata = MyCheck.get_metadata()
    self.assertIsInstance(metadata, dict)
    self.assertIsInstance(metadata['parameters'], list)
    self.assertEqual(len(metadata['parameters']), 2)

  def test_check_declaration_without_result(self):
    class MyCheck(cb.Check):
      title = 'My check'
      description = 'A description'
    # Check class must have at least 1 ResultField.
    with self.assertRaises(errors.NoResultField):
      MyCheck.get_metadata()


class TestSuite(TestCase):

  def test_execute_2_checks_success(self):
    suite = Suite.objects.create()
    check_1 = Check.objects.create(suite=suite, name="CheckDummy")
    check_2 = Check.objects.create(suite=suite, name="CheckDummy")

    # We first create a SuiteExecution object.
    se = SuiteExecution.objects.create(suite=suite, executed=timezone.now())

    # Check 1 is executed.
    check_1.execute(suite_execution=se)
    # It should create a CheckExecution object.
    self.assertEqual(CheckExecution.objects.count(), 1)
    self.assertEqual(CheckExecution.objects.last().check_ref, check_1)
    self.assertEqual(CheckExecution.objects.last().suite_execution, se)
    # It should update the SuiteExecution object.
    # At this point, se is not DONE (only 1 check over 2 has been executed).
    self.assertEqual(se.status, Status.Running)
    # Also, success of the suite execution is not known yet (still 1 check
    # pending).
    self.assertEqual(se.success, None)

    # Check 2 is executed.
    check_2.execute(suite_execution=se)
    # It should create a CheckExecution object.
    self.assertEqual(CheckExecution.objects.count(), 2)
    self.assertEqual(CheckExecution.objects.last().check_ref, check_2)
    self.assertEqual(CheckExecution.objects.last().suite_execution, se)
    # It should update the SuiteExecution object.
    # At this point, se is DONE.
    self.assertEqual(se.status, Status.Done)
    # Now, success is known...
    self.assertEqual(se.success, True)

  def test_execute_2_checks_fail(self):
    suite = Suite.objects.create()
    check_1_failing = Check.objects.create(suite=suite, name="CheckDummy")
    check_2 = Check.objects.create(suite=suite, name="CheckDummy")

    # We first create a SuiteExecution object.
    se = SuiteExecution.objects.create(suite=suite, executed=timezone.now())

    # Check 1 is executed, and it fails (success = False).
    check_1_failing.execute(suite_execution=se, extra_params={'success': False})
    # It should create a CheckExecution object.
    self.assertEqual(CheckExecution.objects.count(), 1)
    self.assertEqual(CheckExecution.objects.last().check_ref, check_1_failing)
    self.assertEqual(CheckExecution.objects.last().suite_execution, se)
    # It should update the SuiteExecution object.
    # At this point, se is not Done (only 1 check over 2 has been executed).
    self.assertEqual(se.status, Status.Running)
    # Also, success of the suite execution is not known yet (still 1 check
    # pending).
    self.assertEqual(se.success, None)

    # Check 2 is executed.
    check_2.execute(suite_execution=se)
    # It should create a CheckExecution object.
    self.assertEqual(CheckExecution.objects.count(), 2)
    self.assertEqual(CheckExecution.objects.last().check_ref, check_2)
    self.assertEqual(CheckExecution.objects.last().suite_execution, se)
    # It should update the SuiteExecution object.
    # At this point, se is Done.
    self.assertEqual(se.status, Status.Done)
    # Now, success is known...
    self.assertEqual(se.success, False)

  def test_execute_with_inactive_checks(self):
    suite = Suite.objects.create()
    Check.objects.create(suite=suite, name="CheckDummy")
    Check.objects.create(suite=suite, name="CheckDummy", active=False)
    Check.objects.create(suite=suite, name="CheckDummy", active=False)

    se = SuiteExecution.objects.create(suite=suite, executed=timezone.now())
    se = suite.execute()

    # Only 1 check should have been executed (2 and 3 and not active).
    self.assertEqual(se.check_executions.count(), 1)
    # Given check_1 succeded, suite success should be True.
    self.assertEqual(se.success, True)


class TestApiCache(TestCase):

  def test_load(self):
    api_cache = ApiCache.load()
    self.assertIsInstance(api_cache, ApiCache)
    self.assertEqual(api_cache.id, 1)

  def test_update(self):
    ApiCache.load().update(ga_accounts_json="[{}]")
    self.assertEqual(ApiCache.objects.count(), 1)
    self.assertEqual(ApiCache.load().ga_accounts, [{}])


if __name__ == '__main__':
    unittest.main()