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

"""Settings used when the application is executed in production mode.

Note: dev/prod mode is infered using the `GAE_APPLICATION` environment variable
value. You can change this beahivour by editing `/project/settings/__init__.py`
file.
"""

from .base import *

# SECURITY WARNING: App Engine's security features ensure that it is safe to
# have ALLOWED_HOSTS = ['*'] when the app is deployed. If you deploy a Django
# app not on App Engine, make sure to set an appropriate host here.
# See https://docs.djangoproject.com/en/2.1/ref/settings/
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '/cloudsql/' + DQM_CLOUDSQL_CONNECTION_NAME,
        'NAME': DQM_CLOUDSQL_DATABASE,
        'USER': DQM_CLOUDSQL_USER,
        # 'PASSWORD': DQM_CLOUDSQL_PASSWORD,
    }
}
