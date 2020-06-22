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


class CheckNbrEventCategories(Check):
  """Detect if any view is measuring enough user actions.

  GIVEN
  An Event
  WHEN
  A query to GA Reporting API v4, filtering on (""ga:eventCategory"" dimension,
  ""ga:totalEvents"" metric) returns 4 or less unique results
  THEN
  The view should be flagged as not measuring enough user actions
  """
  title = '5 event categories'
  description = 'Detect if any view is measuring enough user actions.'
  platform = Platform.Ga
  theme = Theme.Trustful
  parameters = [
    Parameter(name='viewId', data_type=DataType.STRING, delegate=True),
    Parameter(name='startDate', data_type=DataType.DATE, delegate=True),
    Parameter(name='endDate', data_type=DataType.DATE, delegate=True),
    Parameter(name='min_nbr_event_categories',
      title='Min number of event categories',
      data_type=DataType.INT,
      default=5),
  ]
  result_fields = [
    ResultField(name='nbr_event_categories',
      title='Number of event caterogies',
      data_type=DataType.INT),
  ]

  def run(self, params):
    params = self.validate_values(params)

    event_categories = analytics.get_event_categories(
      view_id=params['viewId'],
      start_date=params['startDate'],
      end_date=params['endDate'])

    nbr_event_categories = len(event_categories)

    if nbr_event_categories < params['min_nbr_event_categories']:
      errors = [{'nbr_event_categories': '{} (should be at least {})'.format(
        nbr_event_categories, params['min_nbr_event_categories'])}]
    else:
      errors = []

    return Result(success=not errors, payload=errors)