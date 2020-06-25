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

"""A simple utility wrapper over Google Analytics APIs.

Useful resources:
- https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/webproperties/list
- https://ga-dev-tools.appspot.com/query-explorer/
"""

from datetime import date
from typing import Dict, List, Optional
from urllib.parse import parse_qs
import urllib.parse as urlparse

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from django.conf import settings


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']


def get_service(api: str, version: str) -> None:
  """Build a service to access GA API.

  Requires a service account credentials files.
  See: https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/service-py
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
    settings.SERVICE_ACCOUNT_FILE, SCOPES)
  return build(api, version, credentials=credentials)


def get_accounts() -> List[Dict]:
  """Build a list of all accounts that have been granted access to DQM.

  Each item of the list is a tree containing all nested web properties,
  containing in turn all nested views.

  Example:
  [
     {
        'id': '123456',
        'name': 'My Account',
        # ...
        'webProperties': [
           {
              'id': 'UA-123456-7',
              'name': 'My property name',
              # ...
              'views': [
                 {
                    'id': '123456',
                    'name': 'My view name',
                 },
              ]
        #...
  """
  service = get_service('analytics', 'v3')

  try:
    accounts_data = service.management().accounts().list().execute()
    accounts = accounts_data['items']
  except:
    # GA API will throw an exception is User does not have any Google Analytics
    # account.
    accounts = []

  if accounts:
    properties_data = (service.management().webproperties()
                        .list(accountId='~all').execute())
    properties = properties_data['items'] if 'items' in properties_data else []
  else:
    properties = []

  if properties:
    views_data = (service.management().profiles()
                    .list(accountId='~all', webPropertyId='~all').execute())
    views = views_data['items'] if 'items' in views_data else []
  else:
    views = []

  result = [{
    **a,
    **{'webProperties': [{
        **p,
        **{'views': [v for v in views if v['webPropertyId'] == p['id']]}

      } for p in properties if p['accountId'] == a['id']
    ]}
  } for a in accounts]

  return result


def get_account(account_id: str) -> Optional[Dict]:
  accounts = get_accounts()
  account = [a for a in accounts if a['id'] == account_id]
  return account[0] if account else None


def get_url_parameters(view_id,
  start_date: date,
  end_date: date) -> List[Dict[str, str]]:

  service = get_service('analyticsreporting', 'v4')
  query = {
    'reportRequests': [{
      'viewId': view_id,
      'dateRanges': [{
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d')}],
      'metrics': [{'expression': 'ga:hits'}],
      'dimensions': [{'name': 'ga:pagePath'}]
    }]
  }
  response = service.reports().batchGet(body=query).execute()
  try:
    urls_and_parameters = [{
      'url': url['dimensions'][0],
      'params': parse_qs(urlparse.urlparse(url['dimensions'][0]).query)
      } for url in response['reports'][0]['data']['rows']
        if '?' in url['dimensions'][0]]
  except:
    urls_and_parameters = []

  return urls_and_parameters


def get_referrers(view_id, start_date: date, end_date: date):
  service = get_service('analyticsreporting', 'v4')

  query = {
    'reportRequests': [{
      'viewId': view_id,
      'dateRanges': [{
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d')}],
      'metrics': [{'expression': 'ga:hits'}],
      'dimensions': [{'name': 'ga:fullReferrer'}]
    }]
  }
  response = service.reports().batchGet(body=query).execute()
  try:
    data = [(r['dimensions'][0], int(r['metrics'][0]['values'][0]))
            for r in response['reports'][0]['data']['rows']]
  except:
    data = []

  return data


def get_custom_dims(account_id, web_property_id):
  service = get_service('analytics', 'v3')

  results = service.management().customDimensions().list(
      accountId=account_id,
      webPropertyId=web_property_id).execute()

  return results.get('items', [])


def get_hostnames(view_id,
  start_date: date,
  end_date: date) -> List[Dict[str, str]]:

  service = get_service('analyticsreporting', 'v4')

  query = {
    'reportRequests': [{
      'viewId': view_id,
      'dateRanges': [{
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d')}],
      'metrics': [{'expression': 'ga:hits'}],
      'dimensions': [{'name': 'ga:hostname'}]
    }]
  }
  response = service.reports().batchGet(body=query).execute()

  try:
    hosts = [{'host': r['dimensions'][0], 'hits': r['metrics'][0]['values'][0]}
            for r in response['reports'][0]['data']['rows']]
  except:
    hosts = []

  return hosts


def get_event_categories(view_id,
  start_date: date,
  end_date: date) -> List[Dict[str, str]]:

  service = get_service('analyticsreporting', 'v4')

  query = {
    'reportRequests': [{
      'viewId': view_id,
      'dateRanges': [{
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d')}],
      'metrics': [{'expression': 'ga:totalEvents'}],
      'dimensions': [{'name': 'ga:eventCategory'}]
    }]
  }
  response = service.reports().batchGet(body=query).execute()
  items_count = int(response['reports'][0]['data']['totals'][0]['values'][0])

  if items_count:
    event_categories = [{
      'host': r['dimensions'][0],
      'hits': r['metrics'][0]['values'][0]}
      for r in response['reports'][0]['data']['rows']]
  else:
    event_categories = []

  return event_categories
