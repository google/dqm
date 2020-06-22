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
  GaLevel,
  Parameter,
  Platform,
  Result,
  ResultField,
  Theme,
)
from dqm.helpers import analytics


class CheckCustomDimensions(Check):
  """Verify a list of custom dimensions to be tracked in GA.

  GIVEN
  An Event
  WHEN
  A query to GA Reporting API v4, filtering on ("ga:eventCategory"
  dimension, "ga:totalEvents" metric) returns 4 or less unique results
  THEN
  The view should be flagged as not measuring enough user actions.
  """
  title = 'Custom dimensions'
  description = 'Verify a list of custom dimensions to be tracked in GA.'
  platform = Platform.Ga
  ga_level = GaLevel.Property
  theme = Theme.Insightful
  parameters = [
      Parameter(name='accountId', data_type=DataType.STRING, delegate=True),
      Parameter(name='webPropertyId', data_type=DataType.STRING, delegate=True),
      Parameter(name='customDimNames', title='Custom dimension names to ckeck',
        data_type=DataType.LIST, delegate=False),
  ]
  result_fields = [
      ResultField(name='customDimName', title='Custom dimension name',
        data_type=DataType.STRING),
      ResultField(name='problem', title='Problem detected',
        data_type=DataType.STRING)
  ]

  def run(self, params):
    params = self.validate_values(params)

    customDimNames = params['customDimNames']
    assert type(customDimNames) == list

    property_custom_dims = analytics.get_custom_dims(
      account_id=params['accountId'],
      web_property_id=params['webPropertyId'])

    property_custom_dims_names = [d['name'] for d in property_custom_dims]

    dims_not_present = [{'customDimName': d, 'problem': 'Not found'}
      for d in customDimNames if d not in property_custom_dims_names]

    return Result(success=not dims_not_present, payload=dims_not_present)
