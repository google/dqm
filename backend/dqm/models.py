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

from __future__ import annotations
from dataclasses import asdict
from datetime import date, timedelta
import json
import logging
import traceback
from typing import Any, Dict, List

from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.functions import Trunc
from django.utils import timezone
from dqm.apps import DqmConfig
from dqm.check_bricks import Check as BaseCheck, GaLevel, Platform, Result
from dqm.errors import CheckClassNotFoundError


logger = logging.getLogger(__name__)


class Status(models.IntegerChoices):
  Created = 0
  Running = 1
  Done = 2
  Failed = 3


class SingletonModel(models.Model):
  class Meta:
    abstract = True

  @classmethod
  def load(cls) -> SingletonModel:
    obj, _ = cls.objects.get_or_create(pk=1)
    return obj

  @classmethod
  def update(cls, **kwargs) -> SingletonModel:
    try:
      obj = cls.objects.get(pk=1)
      cls.objects.update(**kwargs)
    except cls.DoesNotExist:
      obj = cls.objects.create(**kwargs)
    return obj


class AppSettings(SingletonModel):
  ga_service_account = models.CharField(max_length=255)
  authorized_emails = models.TextField(null=True, blank=True)


class ApiCache(SingletonModel):
  ga_accounts_json = models.TextField(null=True, blank=True)

  @property
  def ga_accounts(self) -> List[Any]:
    return json.loads(
      self.ga_accounts_json) if self.ga_accounts_json else []


class Suite(models.Model):
  name = models.CharField(max_length=100)

  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return self.name

  def execute(self) -> SuiteExecution:
    se = SuiteExecution.objects.create(suite=self, executed=timezone.now())

    for c in self.checks.filter(active=True):
      check_class = c.check_class()
      check_metadata = check_class.get_metadata()
      specific_params = {}

      # If Google Analytics related, we attach GA params
      if check_metadata['platform'] == Platform.Ga.value:
        ga_scope = self.ga_params.scope

        # Scope dict should be updated if check is at 'property' or 'account'
        # level:
        if check_metadata['ga_level'] == GaLevel.Property.value:
          for item in ga_scope:
            del item['viewId']
          ga_scope = [dict(t) for t in {tuple(d.items()) for d in ga_scope}]
        elif check_metadata['ga_level'] == GaLevel.Account.value:
          ga_scope = [{'accountId': item} for item in list(
            set([item['accountId'] for item in ga_scope]))]

        for scope_dict in ga_scope:
          specific_params = dict(scope_dict, **{
            'startDate': self.ga_params.start_date,
            'endDate': self.ga_params.end_date})

      c.execute(suite_execution=se, extra_params=specific_params)

    return se


class GaParams(models.Model):
  """
  >>> ga_params = GaParams.objects.create(
        scope_json='[
          {
            "viewId":"123456",
            "webPropertyId":"123456",
            "accountId":"12346",
          },
        ]'
      )
  """
  suite = models.OneToOneField(Suite, related_name='ga_params',
    on_delete=models.CASCADE)
  scope_json = models.TextField(default='[]')
  start_date = models.DateField(default=timezone.now() - timedelta(days=30))
  end_date = models.DateField(auto_now_add=True)

  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def to_dict(self) -> Dict:
    return {
      'scope': self.scope,
      'startDate': self.start_date,
      'endDate': self.end_date
    }

  @property
  def scope(self) -> List[Any]:
    return json.loads(self.scope_json) if self.scope_json else []

  @property
  def views(self) -> List[str]:
    return [s['viewId'] for s in json.loads(self.scope_json)]


class SuiteExecution(models.Model):
  suite = models.ForeignKey(Suite, on_delete=models.CASCADE,
    related_name='executions')
  status = models.IntegerField(choices=Status.choices, default=Status.Created)
  success = models.BooleanField(null=True, blank=True)
  executed = models.DateTimeField(null=True, blank=True)

  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return '{}, {}'.format(self.suite, self.executed)

  def update_after_check_execution(self, check_execution) -> None:
    """
    This method if called after every check execution.

    It updates the status of the SuiteExecution object so that it can reflect
    the actual status (even if checks a executed asynchronously).
    """
    nbr_active_checks = self.suite.checks.filter(active=True).count()
    check_executions = self.check_executions.all()
    checks_finished = [ce.status == Status.Done for ce in check_executions]
    results = [ce.success == True for ce in check_executions]

    # If we have the same number of finished checks than the total number of
    # active checks in the suite, then we are done.
    if len(checks_finished) == nbr_active_checks:
      self.status = Status.Done
      self.success = all(results)
    else:
      # ...else, we're still running, and success is still undefinied (None).
      self.status = Status.Running

    self.save()

  @classmethod
  def get_stats(cls) -> List:
    query = SuiteExecution.objects.filter(
      executed__gte=timezone.now()-timedelta(days=10)).annotate(
      day=Trunc('executed', 'day', output_field=models.DateField()))

    results = [['day', 'executions', 'successes', 'fails']]
    results = results + [[
      date(day.year, day.month, day.day),
      len([se for se in query if date(se.day.year, se.day.month,
        se.day.day) == date(day.year, day.month, day.day)]),
      len([se for se in query if se.success and date(se.day.year,
        se.day.month, se.day.day) == date(day.year, day.month, day.day)]),
      len([se for se in query if not se.success and date(se.day.year,
        se.day.month, se.day.day) == date(day.year, day.month, day.day)]),
    ] for day in (
      timezone.now() - timedelta(days=10) + timedelta(n) for n in range(11))]

    return results


class Check(models.Model):
  """The Django model for a check.

  Please note that we thus have 2 different `Check` classes in the application:
  - This class, used internally for persistence and runtime execution.
  - The `check_bricks.Check` class, used by developpers as a base class to build
    new checks (see `/checks/` for examples of checks implementations).
  """
  suite = models.ForeignKey(Suite, on_delete=models.CASCADE,
    related_name='checks')
  name = models.CharField(max_length=50, choices=DqmConfig.checks)
  params_json = models.TextField(null=True, blank=True)
  comments = models.TextField(null=True, blank=True)
  active = models.BooleanField(default=True)

  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return self.name

  @classmethod
  def get_checks_metadata(cls) -> List[Dict]:
    """Build a list of dictonnaries describing the metadata for all available
    checks. Relies on the `get_metadata` class method from base `Check` class.

    Example of result:
    [
      {
        'name': 'MyCheck',
        'title': 'My super check',
        'description': 'The description of my check',
        'theme': 'trustful',
        'platform': 'ga',
        'ga_level': 'view',
        'parameters': [{
          'name': 'viewId',
          'data_type': 'str',
          'title': '',
          'default': None, 'delegate': True}],
        'resultFields': [{'name': 'url', 'title': 'URL', 'data_type': 'str'}]
      },
      # ...
    ]
    """
    checks_registry = apps.get_app_config('dqm').checks
    check_classes = [cc for name, cc in checks_registry.items()]
    checks_metadata = [c.get_metadata() for c in check_classes]
    return checks_metadata

  @property
  def params(self) -> Dict:
    return json.loads(self.params_json) if self.params_json else {}

  @property
  def check_class(self) -> BaseCheck:
    """Returns the actual check class (BaseCheck) for the current check object.
    """
    checks_registry = apps.get_app_config('dqm').checks
    try:
      check_class = checks_registry[self.name]
    except:
      raise CheckClassNotFoundError(check_name=self.name)

    return check_class

  def execute(self,
    suite_execution: SuiteExecution,
    extra_params: Dict = None) -> CheckExecution:
    """Execute the check and return a CheckExecution object by execution the
    `run`method of the base check class of this check object.

    A CheckExecution is created and persisted in database.

    Note that every `CheckExecution` is part of a `SuiteExecution`, the related
    `SuiteExecution`object is thus also updated in this method.
    """

    ce = CheckExecution.objects.create(suite_execution=suite_execution,
      check_ref=self)
    params = {**self.params, **extra_params} if extra_params else self.params

    try:
      result: Result = self.check_class().run(params=params)

      ce.input_data_json = json.dumps(params, cls=DjangoJSONEncoder)
      ce.result_json = json.dumps(asdict(result), cls=DjangoJSONEncoder)
      ce.status = Status.Done
      ce.success = ce.result['success']
    except Exception as e:
      logger.error(traceback.format_exc())
      ce.result_json = json.dumps({'exception': str(e)}, cls=DjangoJSONEncoder)
      ce.status = Status.Failed
    finally:
      ce.save()
      suite_execution.update_after_check_execution(check_execution=ce)

    return ce


class CheckExecution(models.Model):
  check_ref = models.ForeignKey(Check, on_delete=models.CASCADE)
  suite_execution = models.ForeignKey(SuiteExecution, on_delete=models.CASCADE,
    related_name='check_executions', null=True, blank=True)
  status = models.IntegerField(choices=Status.choices, default=Status.Created)
  success = models.BooleanField(null=True, blank=True)
  input_data_json = models.TextField(null=True, blank=True)
  result_json = models.TextField(null=True, blank=True)

  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return '{} - {}'.format(self.check_ref, self.get_status_display())

  @property
  def result(self) -> List[Any]:
    return json.loads(self.result_json) if self.result_json else []

  @classmethod
  def get_stats(cls) -> List:
    query = CheckExecution.objects.filter(
      created__gte=timezone.now()-timedelta(days=10)).annotate(
      day=Trunc('created', 'day', output_field=models.DateField()))

    results = [['day', 'executions', 'successes', 'fails']]
    results = results + [[
      date(day.year, day.month, day.day),
      len([se for se in query if date(se.day.year, se.day.month,
        se.day.day) == date(day.year, day.month, day.day)]),
      len([se for se in query if se.success and date(se.day.year, se.day.month,
        se.day.day) == date(day.year, day.month, day.day)]),
      len([se for se in query if not se.success and date(se.day.year,
        se.day.month, se.day.day) == date(day.year, day.month, day.day)]),
    ] for day in (
      timezone.now() - timedelta(days=10) + timedelta(n) for n in range(11))]

    return results