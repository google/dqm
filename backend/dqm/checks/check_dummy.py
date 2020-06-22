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

from dqm.check_bricks import Check, DataType, Parameter, Result, ResultField


class CheckDummy(Check):
  """A simple no-op "dummy" check.

  >>> CheckDummy().run(params={})
  Result(payload=[], success=True)
  >>> CheckDummy().run(params={'success': False, 'problems': 'Oops,Too bad'})
  Result(payload=['Oops', 'Too bad'], success=False)
  """
  title = 'No op dummy check'
  description = """
  This check does nothing but returning a result from parameters.
  You can use it to test a brand new suite!
  """
  parameters = [
    Parameter(name='success', title='Is that a success?',
      data_type=DataType.BOOLEAN, default=True),
    Parameter(name='problems', title='List of problems',
      data_type=DataType.LIST, default=[]),
  ]
  result_fields = [
    ResultField(name='problem', title='Problem', data_type=DataType.STRING),
  ]

  def run(self, params):
    params = self.validate_values(params)

    return Result(success=params['success'],
      payload=[{'problem': p} for p in params['problems']])

