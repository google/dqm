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

"""URL dispatcher for DQM project.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path


admin.site.site_header = 'DQM'

urlpatterns = [
    path('', include('dqm.urls')),
    # path('admin/', admin.site.urls),
]

if settings.DEBUG:
  from django.conf import settings
  import debug_toolbar
  urlpatterns = [
      path('__debug__/', include(debug_toolbar.urls)),
  ] + urlpatterns
