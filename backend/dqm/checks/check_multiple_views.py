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


class CheckMultipleViews(Check):
  """Detect if multiple views in one property (should be at least 2 views per
  property).

  Leverage multiple views within a property to store different datasets and
  allow for testing without affecting the main source of truth.

  Minimum of 2 views required (production, raw).
  """
  title = 'Multiple views in property'
  description = """
  Detect if multiple views in one property (should be at least 2 views per
  property).
  """
  platform = Platform.Ga
  ga_level = GaLevel.Property
  theme = Theme.Trustful
  parameters = [
    Parameter(name='accountId', data_type=DataType.STRING, delegate=True),
    Parameter(name='webPropertyId', data_type=DataType.STRING, delegate=True),
    Parameter(name='min_nbr_views_per_property',
      title='Min number of views per property',
      data_type=DataType.INT,
      default=2),
  ]
  result_fields = [
    ResultField(name='property_id', title='Property Id',
      data_type=DataType.STRING),
    ResultField(name='property_name', title='Property name',
      data_type=DataType.STRING),
    ResultField(name='nbr_views', title='Number of views',
      data_type=DataType.INT),
    ResultField(name='min_nbr_views', title='Required number of views',
      data_type=DataType.INT),
  ]

  def run(self, params):
    params = self.validate_values(params)

    account_data = analytics.get_account(account_id=params['accountId'])
    if not account_data:
      return Result(success=True, payload=[])

    errors = []
    for p in account_data['webProperties']:
      nbr_views = len(p['views'])
      if nbr_views < params['min_nbr_views_per_property']:
        errors.append({
          'property_id': p['id'],
          'property_name': p['name'],
          'nbr_views': nbr_views,
          'min_nbr_views': params['min_nbr_views_per_property'],
        })

    return Result(success=(not errors), payload=errors)