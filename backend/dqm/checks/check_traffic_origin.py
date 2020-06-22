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


class CheckTrafficOrigin(Check):
  """Detect if traffic is referred from major adservers hostnames.

  GIVEN
  A traffic source
  WHEN
  A query to GA Reporting API v4, filtering on (""ga:source"" dimension
  contains ""stats.g.doubleclick.net"" OR ""doubleclick.net"" OR
  ""googleads.g.doubleclick.net"" OR ""tpc.googlesyndication.com"" OR
  ""mail.*"")  returns 1 or more results
  THEN
  The URL should be flagged as potentially traffic from major adserver.
  """
  title = 'Traffic origin'
  description = 'Detect if traffic is referred from major adservers hostnames.'
  platform = Platform.Ga
  theme = Theme.Trustful
  parameters = [
    Parameter(name='viewId', data_type=DataType.STRING, delegate=True),
    Parameter(name='startDate', data_type=DataType.DATE, delegate=True),
    Parameter(name='endDate', data_type=DataType.DATE, delegate=True),
    Parameter(name='adservers_hostnames', title='URLs of adserver hostnames',
      data_type=DataType.LIST,
      default=['stats.g.doubleclick.net', 'doubleclick.net',
        'googleads.g.doubleclick.net', 'tpc.googlesyndication.com', 'mail.']),
  ]
  result_fields = [
    ResultField(name='referrer', title='Referrer', data_type=DataType.STRING),
    ResultField(name='hits', title='Nbr of hits', data_type=DataType.STRING)
  ]

  def run(self, params):
    params = self.validate_values(params)

    adservers_hostnames = params['adservers_hostnames']
    referrers = analytics.get_referrers(
      view_id=params['viewId'],
      start_date=params['startDate'],
      end_date=params['endDate'])

    problems = []
    for ah in adservers_hostnames:
      for r in referrers:
        if ah in r[0]:
          problems.append({
            'referrer': r[0],
            'hits': r[1],
          })

    return Result(success=not problems, payload=problems)