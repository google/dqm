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

"""Base configuration for the DQM project.
"""

import os

import pymysql

# Environment variables
DQM_CLOUDSQL_USER = os.getenv('DQM_CLOUDSQL_USER')
DQM_CLOUDSQL_PASSWORD = os.getenv('DQM_CLOUDSQL_PASSWORD')
DQM_CLOUDSQL_DATABASE = os.getenv('DQM_CLOUDSQL_DATABASE')
DQM_CLOUDSQL_CONNECTION_NAME = os.getenv('DQM_CLOUDSQL_CONNECTION_NAME')
DQM_SQLITE_FILE_PATH = os.getenv('DQM_SQLITE_FILE_PATH', 'db')
SECRET_KEY = os.getenv('DQM_SECRET_KEY', 'unsecuredsecretkey')
SERVICE_ACCOUNT_FILE = os.getenv('DQM_SERVICE_ACCOUNT_FILE_PATH', 'key.json')

DEBUG = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'dqm.apps.DqmConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_ROOT = 'static'
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
# Install PyMySQL as mysqlclient/MySQLdb to use Django's mysqlclient adapter
# See https://docs.djangoproject.com/en/2.1/ref/databases/#mysql-db-api-drivers
# for more information
  # noqa: 402
pymysql.version_info = (1, 4, 1, "final", 0)
pymysql.install_as_MySQLdb()

