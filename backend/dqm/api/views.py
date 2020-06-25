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

"""Django views for DQM API.
"""

from dataclasses import asdict
import json

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from dqm.api.encoders import DqmApiEncoder
from dqm.helpers import analytics
from dqm.models import (
  ApiCache,
  AppSettings,
  Check,
  CheckExecution,
  GaParams,
  Suite,
  SuiteExecution,
)


@csrf_exempt
def app_settings(request):
  app_settings = AppSettings.load()

  return JsonResponse({'appSettings': {
    'gaServiceAccount': app_settings.ga_service_account,
    'authorizedEmails': app_settings.authorized_emails,
  }})


@csrf_exempt
def cache(request):
  cache = ApiCache.load()
  return JsonResponse({'cache': {
    'gaAccounts': cache.ga_accounts
  }})


@csrf_exempt
def ga_accounts(request):
  ga_accounts = analytics.get_accounts()

  accounts = [{
    'id': a['id'],
    'name': a['name'],
    'webProperties': [{
      'id': p['id'],
      'name': p['name'],
      'accountId': p['accountId'],
      'websiteUrl': p['websiteUrl'],
      'views': [{
        'id': v['id'],
        'name': v['name'],
        'accountId': v['accountId'],
        'webPropertyId': v['webPropertyId'],
        'websiteUrl': v['websiteUrl'],
        'type': v['type'],
        'eCommerceTracking': v['eCommerceTracking'],
        'enhancedECommerceTracking': (v['enhancedECommerceTracking']
          if 'enhancedECommerceTracking' in v else False),
        'botFilteringEnabled': v['botFilteringEnabled'],
        'excludeQueryParameters': (v['excludeQueryParameters']
          if 'excludeQueryParameters' in v else False),
        'siteSearchQueryParameters': (v['siteSearchQueryParameters']
          if 'siteSearchQueryParameters' in v else False),
        'stripSiteSearchQueryParameters': (v['stripSiteSearchQueryParameters']
          if 'stripSiteSearchQueryParameters' in v else False),
      } for v in p['views']]
    } for p in a['webProperties']]
  } for a in ga_accounts]

  # Each time we fetch accounts data from the API, we update the cache.
  ApiCache.load().update(
    ga_accounts_json=json.dumps(accounts, cls=DqmApiEncoder))

  return JsonResponse({'gaAccounts': accounts}, encoder=DqmApiEncoder)


@csrf_exempt
def checks_list(request):
  """Endpoint that returns a list of all checks available
  """
  result = Check.get_checks_metadata()
  return JsonResponse({'checksMetadata': result}, encoder=DqmApiEncoder)


def create_suite(request):
  payload = json.loads(request.body)
  suite = Suite.objects.create(name=payload['name'])
  GaParams.objects.create(suite=suite, scope_json='')

  # If user asked for a suite template, we also create all the checks related to
  # this template, linked to the suite.
  if payload['templateId']:
    checks = [c for c in Check.get_checks_metadata()
              if c['theme'] == payload['templateId']]
    for c in checks:
      Check.objects.create(suite=suite, name=c['name'])

  return JsonResponse({'id': suite.id}, encoder=DqmApiEncoder)


def get_suite(request, suite_id):
  suite = get_object_or_404(Suite.objects.prefetch_related('ga_params'),
    pk=suite_id)
  executions = SuiteExecution.objects.filter(suite=suite).prefetch_related(
    'check_executions__check_ref').order_by('-created')
  checks = Check.objects.filter(suite_id=suite.id)
  check_metadata = Check.get_checks_metadata()

  result = {
    'id': suite.id,
    'name': suite.name,
    'created': suite.created,
    'updated': suite.updated,
    'gaParams': {
      'scope': suite.ga_params.scope,
      'startDate': suite.ga_params.start_date,
      'endDate': suite.ga_params.end_date,
    },
    'checks': [{
      'id': c.id,
      'name': c.name,
      'active': c.active,
      'comments': c.comments,
      'checkMetadata': [cm for cm in check_metadata if cm['name'] == c.name],
      'paramValues': c.params,
      # 'resultFields': [asdict(rf) for rf in c.check_class.result_fields],
    } for c in checks],
    'executions': [{
      'id': se.id,
      'success': se.success,
      'executed': se.executed,
      'checkExecutions': [{
        'id': ce.id,
        'title': ce.check_ref.check_class.title,
        'name': ce.check_ref.name,
        'status': ce.get_status_display(),
        'success': ce.success,
        'inputData': json.loads(ce.input_data_json) if ce.input_data_json
                      else {},
        'result': json.loads(ce.result_json) if ce.result_json else {},
      } for ce in se.check_executions.all()]
    } for se in executions]
  }

  return JsonResponse({'suite': result}, encoder=DqmApiEncoder)


def update_suite(request, suite_id):
  payload = json.loads(request.body)
  s = get_object_or_404(Suite, pk=suite_id)
  ga = GaParams.objects.get(id=s.ga_params.id)

  if 'gaParams' in payload:
    ga.scope_json = json.dumps(payload['gaParams']['scope'])
    ga.start_date = payload['gaParams']['startDate']
    ga.end_date = payload['gaParams']['endDate']
    ga.save()

  suite = {
    'id': s.id,
    'name': s.name,
    'gaParams': {
      'scope': s.ga_params.scope,
      'start_date': s.ga_params.start_date,
      'end_date': s.ga_params.end_date,
      'created': s.ga_params.created,
      'updated': s.ga_params.updated,
    },
    'created': s.created,
    'updated': s.updated,
  }

  return JsonResponse({'suite': suite}, encoder=DqmApiEncoder)


def delete_suite(request, suite_id):
  Suite.objects.filter(pk=suite_id).delete()
  return JsonResponse({'status': 'OK'}, encoder=DqmApiEncoder)


def suites_list(request):
  suites = [{
    'id': s.id,
    'name': s.name,
    'created': s.created,
    'updated': s.updated,
    'executions': [{
      'id': se.id,
      'success': se.success,
    } for se in s.executions.all()],
  } for s in Suite.objects.all().prefetch_related(
              'executions').order_by('-created')]

  # Django would issue (n) db queries to deal with the last execution, so we
  # process it in raw Python...
  for s in suites:
    s['lastExecutionSuccess'] = (s['executions'][-1:][0]['success'] == True
                                  if s['executions'][-1:] else None)
    del(s['executions'])

  return JsonResponse({'suites': suites}, encoder=DqmApiEncoder)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def suites(request):
  if request.method == 'POST':
    return create_suite(request)
  else:
    return suites_list(request)


@csrf_exempt
@require_http_methods(['GET', 'PUT', 'DELETE'])
def suite(request, suite_id):
  if request.method == 'PUT':
    return update_suite(request, suite_id)
  elif request.method == 'DELETE':
    return delete_suite(request, suite_id)
  else:
    return get_suite(request, suite_id)


@csrf_exempt
def create_check(request, suite_id):
  payload = json.loads(request.body)

  suite = get_object_or_404(Suite, pk=suite_id)
  c, _ = Check.objects.get_or_create(
    suite=suite,
    name=payload['name'],
    defaults={})

  c.params_json = json.dumps({
    p.name: p.default for p in c.check_class.parameters})

  c.save()

  check = {
    'id': c.id,
    'name': c.name,
    'active': c.active,
    'paramValues': c.params,
    'comments': c.comments,
  }

  return JsonResponse({'check': check}, encoder=DqmApiEncoder)


@csrf_exempt
@require_http_methods(['PUT'])
def update_check(request, suite_id, check_id):
  payload = json.loads(request.body)
  payload['params_json'] = json.dumps(payload.pop('paramValues'))
  try:
    del payload['resultFields']
  except:
    pass
  try:
    del payload['checkMetadata']
  except:
    pass
  Check.objects.filter(id=check_id).update(**payload)
  return JsonResponse({'check': None}, encoder=DqmApiEncoder)


def delete_check(request, suite_id, check_id):
  Check.objects.filter(pk=check_id).delete()
  return JsonResponse({'status': 'OK'}, encoder=DqmApiEncoder)


@csrf_exempt
@require_http_methods(['PUT', 'DELETE'])
def check(request, suite_id, check_id):
  if request.method == 'PUT':
    return update_check(request, suite_id, check_id)
  elif request.method == 'DELETE':
    return delete_check(request, suite_id, check_id)


@csrf_exempt
@require_http_methods(['POST'])
def run_suite(request, suite_id):
  suite = get_object_or_404(Suite.objects.select_related('ga_params'),
                            pk=suite_id)
  se = suite.execute()
  result = {
    'id': se.id,
    'success': se.success,
    'executed': se.executed,
    'checkExecutions': [{
      'id': ce.id,
      'name': ce.check_ref.name,
      'title': ce.check_ref.check_class.title,
      'status': ce.get_status_display(),
      'success': ce.success,
      'inputData': json.loads(ce.input_data_json) if ce.input_data_json else {},
      'result': json.loads(ce.result_json) if ce.result_json else {},
    } for ce in se.check_executions.all()]
  }

  return JsonResponse({'result': result}, encoder=DqmApiEncoder)


def stats_suites_executions(request):
  return JsonResponse({
    'result': SuiteExecution.get_stats()}, encoder=DqmApiEncoder)


def stats_checks_executions(request):
  return JsonResponse({
    'result': CheckExecution.get_stats()}, encoder=DqmApiEncoder)
