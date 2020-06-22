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

"""Error classes uses by DQM core.
"""

class CheckClassNotFoundError(Exception):
  def __init__(self, check_name):
      self.check_name = check_name

  def __str__(self):
    return '[{}] Class is not defined in checks module'.format(self.check_name)


class CheckNotImplementedError(NotImplementedError):
  def __init__(self, check_name):
      self.check_name = check_name

  def __str__(self):
    return '[{}] Class has no run method'.format(self.check_name)


class BadParametersError(RuntimeError):
  def __init__(self, check_name):
    self.check_name = check_name

  def __str__(self):
    return '[{}] Check parameters are not set correctly'.format(self.check_name)


class MissingMetadata(RuntimeError):
  def __init__(self, check_name, attr):
    self.check_name = check_name
    self.attr = attr

  def __str__(self):
    return ('[{check_name}] Missing metatadata: "{attr}" '
            'is required in check class').format(
              check_name=self.check_name,
              attr=self.attr)


class NoResultField(RuntimeError):
  def __init__(self, check_name):
    self.check_name = check_name

  def __str__(self):
    return '[{}] Check should have at least 1 result field'.format(
      self.check_name)


class BadDefaultValueTypeError(RuntimeError):
  def __init__(self, name, expected, got):
    self.name = name
    self.expected = expected
    self.got = got

  def __str__(self):
    return ('Bad default value type for parameter "{name}" '
            '(expected: {expected}, got: {got})').format(
                name=self.name,
                expected=self.expected,
                got=self.got)


class MissingParameterValueError(RuntimeError):
  def __init__(self, name, data_type):
    self.name = name
    self.data_type = data_type

  def __str__(self):
    return 'Missing value for parameter "{name}" (type: {data_type})'.format(
      data_type=self.data_type,
      name=self.name)


class BadResultFielsError(RuntimeError):
  def __init__(self, check_name):
    self.check_name = check_name

  def __str__(self):
    return '[{}] Check result fields are not set correctly'.format(
      self.check_name)
