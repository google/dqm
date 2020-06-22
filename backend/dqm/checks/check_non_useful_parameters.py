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

from dqm.check_bricks import (
  Check,
  DataType,
  Parameter,
  Platform,
  Result,
  ResultField,
  Theme,
)
from dqm.helpers import analytics


class CheckNonUsefulParameters(Check):
  """Detect tracked URLs containing non useful parameters.

  GIVEN
  A site URL
  WHEN
  A query to GA Reporting API v4, filtering on (""ga:pagePath"" dimension
  contains ""msclkid="" OR ""fbclid="" OR ""token="" OR ""vid="" OR ""cid=""
  OR ""mt_*="" OR ""efid ="")  returns 1 or more results
  THEN
  The URL should be flagged as potentially non-useful.
  """
  title = 'Non useful URI parameters'
  description = """
  Detect tracked URLs containing non useful parameters, such as msclkid, fbclid,
  token, vid, cid or mt_*.
  """
  platform = Platform.Ga
  theme = Theme.Trustful
  parameters = [
    Parameter(name='viewId', data_type=DataType.STRING, delegate=True),
    Parameter(name='startDate', data_type=DataType.DATE, delegate=True),
    Parameter(name='endDate', data_type=DataType.DATE, delegate=True),
    Parameter(name='blackList',
      title='Parameters blacklist',
      data_type=DataType.LIST,
      default=['msclkid', 'fbclid', 'token', 'vid', 'cid']),
  ]
  result_fields = [
    ResultField(name='url', title='URL', data_type=DataType.STRING),
    ResultField(name='param', title='Parameter name', data_type=DataType.STRING)
  ]

  def run(self, params):
    params = self.validate_values(params)

    black_list = params['blackList']
    urls = analytics.get_url_parameters(
      view_id=params['viewId'],
      start_date=params['startDate'],
      end_date=params['endDate'])

    # TODO: add "mt_*="
    problems = []
    for url in urls:
      for p in url['params']:
        if p in black_list:
          problems.append({
            'url': url['url'],
            'param': p,
          })

    return Result(success=not problems, payload=problems)