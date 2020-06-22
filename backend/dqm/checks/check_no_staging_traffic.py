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

import re

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


class CheckNoStagingTraffic(Check):
  """Detect if data collection is coming from staging hostname.

  GIVEN
  A site Hostname
  WHEN
  A query to GA Reporting API v4, filtering on ("ga:hostname" dimension
  matches Regexp "^test.*" OR "^preprod.*" OR "^staging.*" OR "^uat.*")
  returns 1 or more results
  THEN
  The URL should be flagged as potentially traffic from staging
  hostnames.
  """
  title = 'Staging traffic'
  description = 'Detect if data collection is coming from staging hostname.'
  platform = Platform.Ga
  theme = Theme.Trustful
  parameters = [
    Parameter(name='viewId', data_type=DataType.STRING, delegate=True),
    Parameter(name='startDate', data_type=DataType.DATE, delegate=True),
    Parameter(name='endDate', data_type=DataType.DATE, delegate=True),
    Parameter(name='staging_hosts',
      title='Regexp to match staging hosts',
      data_type=DataType.LIST,
      default=['^test.*', 'preprod.*', '^staging.*', '^uat.*']),
  ]
  result_fields = [
    ResultField(name='host', title='Hostname', data_type=DataType.STRING),
    ResultField(name='hits', title='Nbr of hits', data_type=DataType.STRING)
  ]

  def run(self, params):
    params = self.validate_values(params)

    hosts = analytics.get_hostnames(
      view_id=params['viewId'],
      start_date=params['startDate'],
      end_date=params['endDate'])

    try:
      blacklist = [re.compile(p) for p in params['staging_hosts']]
    except Exception as e:
      raise Exception('Some of your regex are failing to compile: {}'.format(e))

    errors = [h for h in hosts if any(regex.match(h['host'])
      for regex in blacklist)]

    return Result(success=not errors, payload=errors)
