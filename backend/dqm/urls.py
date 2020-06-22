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

"""URL dispatcher for DQM app.
"""

from django.urls import include, path

from dqm.api import views

urlpatterns = [
  path('api/', include([
    path('cache', views.cache),
    path('gaaccounts', views.ga_accounts),
    path('appsettings', views.app_settings),

    path('suites/', include([
      path('', views.suites),
      path('<int:suite_id>', views.suite),
      path('<int:suite_id>/run', views.run_suite),
      path('<int:suite_id>/checks', views.create_check),
      path('<int:suite_id>/checks/<int:check_id>', views.check),
      path('stats', views.stats_suites_executions),
    ])),

    path('checks/', include([
      path('', views.checks_list),
      path('stats', views.stats_checks_executions),
    ])),
  ])),
]

