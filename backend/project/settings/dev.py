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

"""Settings used when the application is executed in development mode.

Note: dev/prod mode is infered using the `GAE_APPLICATION` environment variable
value. You can change this beahivour by editing `/project/settings/__init__.py`
file.
"""

import os
from .base import *

DEBUG = True

INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'debug_toolbar_force.middleware.ForceDebugToolbarMiddleware',
] + MIDDLEWARE


# Running locally so connect to either a local MySQL instance or connect to
# Cloud SQL via the proxy. To start the proxy via command line:
#     $ cloud_sql_proxy -instances=[INSTANCE_CONNECTION_NAME]=tcp:3306
# See https://cloud.google.com/sql/docs/mysql-connect-proxy
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': DQM_CLOUDSQL_DATABASE,
        'USER': DQM_CLOUDSQL_USER,
        # 'PASSWORD': DQM_CLOUDSQL_PASSWORD,
    }
}

# Alternatively, to speed up dev and avoid GCP connections, you can simply use
# a SQLite database.
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': DQM_SQLITE_FILE_PATH, # Defaults to './db'
#     }
# }

CORS_ORIGIN_WHITELIST = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

INTERNAL_IPS = [
    '127.0.0.1',
]
