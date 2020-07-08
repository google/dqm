#!/usr/bin/env python3
from enum import Enum
import time
import subprocess
import os
import sys


class Color(Enum):
  HEADER = '\033[95m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  ORANGE = '\033[93m'
  RED = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


def text_color(text, color, space_before=True):
  return '{space}{color}{text}{end}'.format(space='\n' if space_before else '', color=color.value, text=text, end='\033[0m')


def abort():
  print(text_color('Deployment canceled.', Color.RED))
  sys.exit(0)


if __name__ == '__main__':
  print(text_color('┌────────────────────────────────────────────────┐', Color.HEADER, space_before=False))
  print(text_color('│ Welcome to Data Quality Manager GCP installer! │', Color.HEADER, space_before=False))
  print(text_color('└────────────────────────────────────────────────┘', Color.HEADER, space_before=False))

  project_id = subprocess.check_output(['gcloud', 'config', 'list', '--format', 'value(core.project)']).decode('utf-8').replace('\n','')

  prompt = input(text_color('You are about to deploy DQM within GCP project "{}", continue? (Y/n) '.format(project_id), Color.BOLD))
  if prompt.lower() == 'n':
    abort()

  print(text_color('Downloading sources...', Color.BLUE))
  subprocess.check_output(['git', 'clone', 'https://github.com/google/dqm.git'])

  print(text_color('Installing frontend dependencies...', Color.BLUE))
  subprocess.check_output(['npm', 'install'], cwd='dqm/frontend')

  print(text_color('Building frontend (it can take a little while)...', Color.BLUE))
  subprocess.check_output(['npm', 'run', 'build'], cwd='dqm/frontend')

  print(text_color('Installing pipenv...', Color.BLUE))
  subprocess.check_output(['pip3', 'install', '--user', 'pipenv'])

  print(text_color('Installing Python libs...', Color.BLUE))
  subprocess.check_output(['python3', '-m', 'pipenv', 'install', '--dev'], cwd='dqm/backend')

  print(text_color('Enabling APIs...', Color.BLUE))
  subprocess.check_output(['gcloud', 'services', 'enable', 'analytics.googleapis.com'])
  subprocess.check_output(['gcloud', 'services', 'enable', 'analyticsreporting.googleapis.com'])

  print(text_color('Creating App Engine application...', Color.BLUE))
  try:
    subprocess.check_output(['gcloud', 'app', 'create'])
  except subprocess.CalledProcessError as e:
    print(text_color('Failed to create App Engine app (this is normal if you have an existing app).', Color.ORANGE))
    prompt = input(text_color('Continue anyway and deploy on existing app? (Y/n) ', Color.BOLD))
    if prompt.lower() == 'n':
      abort()

  print(text_color('Getting service account key...', Color.BLUE))
  subprocess.check_output(['gcloud', 'iam', 'service-accounts', 'keys', 'create', './key.json', '--iam-account', f'{project_id}@appspot.gserviceaccount.com'], cwd='dqm/backend')

  print(text_color('Setting up database...', Color.BLUE))

  prompt = input(text_color('Do you want to reuse an existing SQL instance? (y/N) ', Color.BOLD))
  create_sql_instance = True if prompt.lower() != 'y' else False
  sql_instance_name = input(text_color('SQL instance name (dqm)? ', Color.BOLD)) or 'dqm'
  sql_instance_region = input(text_color('SQL instance region (europe-west1)? ', Color.BOLD)) or 'europe-west1'
  if create_sql_instance:
    print(text_color('Creating SQL instance (it can take a little while)...', Color.BLUE))
    subprocess.check_output(['gcloud', 'sql', 'instances', 'create', sql_instance_name, '--region={}'.format(sql_instance_region)])

  prompt = input(text_color('Do you want to reuse an existing MySQL database? (y/N) ', Color.BOLD))
  create_sql_db = True if prompt.lower() != 'y' else False
  sql_db_name = input(text_color('MySQL database name (dqm)? ', Color.BOLD)) or 'dqm'
  if create_sql_db:
    print(text_color('Creating MySQL database...', Color.BLUE))
    subprocess.check_output(['gcloud', 'sql', 'databases', 'create', sql_db_name, '--instance={}'.format(sql_instance_name)])

  prompt = input(text_color('Do you want to reuse an existing MySQL user? (y/N) ', Color.BOLD))
  create_sql_user = True if prompt.lower() != 'y' else False
  sql_user_name = input(text_color('MySQL user name (dqmuser)? ', Color.BOLD)) or 'dqmuser'
  if create_sql_user:
    print(text_color('Creating MySQL user...', Color.BLUE))
    subprocess.check_output(['gcloud', 'sql', 'users', 'create', sql_user_name, '--instance={}'.format(sql_instance_name)])

  print(text_color('Connecting to database...', Color.BLUE))
  subprocess.check_output(['wget', 'https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64', '-O', 'cloud_sql_proxy'], cwd='dqm/backend')
  subprocess.check_output(['chmod', '+x', 'cloud_sql_proxy'], cwd='dqm/backend')
  connection_name = f'{project_id}:{sql_instance_region}:{sql_instance_name}'
  subprocess.Popen(['./cloud_sql_proxy', f'-instances={connection_name}=tcp:3306'], stdout=subprocess.PIPE, cwd='dqm/backend')

  # Wait for database connection to be available...
  time.sleep(4)

  print(text_color('Migrating database...', Color.BLUE))
  os.putenv('DQM_CLOUDSQL_CONNECTION_NAME', connection_name)
  os.putenv('DQM_CLOUDSQL_DATABASE', sql_db_name)
  os.putenv('DQM_CLOUDSQL_USER', sql_user_name)
  subprocess.check_output(['python3', '-m', 'pipenv', 'run', 'python', 'manage.py', 'makemigrations'], cwd='dqm/backend')
  subprocess.check_output(['python3', '-m', 'pipenv', 'run', 'python', 'manage.py', 'makemigrations', 'dqm'], cwd='dqm/backend')
  subprocess.check_output(['python3', '-m', 'pipenv', 'run', 'python', 'manage.py', 'migrate'], cwd='dqm/backend')

  print(text_color('Generating requirements.txt file...', Color.BLUE))
  with open('dqm/backend/requirements.txt', 'w') as f:
    subprocess.call(['python3', '-m', 'pipenv', 'lock', '--requirements'], cwd='dqm/backend', stdout=f)

  print(text_color('Updating app.yaml file...', Color.BLUE))
  with open('dqm/backend/app.yaml') as f:
    content = f.read()
    content = content.replace('DQM_CLOUDSQL_CONNECTION_NAME: ""', f'DQM_CLOUDSQL_CONNECTION_NAME: "{connection_name}"')
    content = content.replace('DQM_CLOUDSQL_USER: "dqmuser"', f'DQM_CLOUDSQL_USER: "{sql_user_name}"')
    content = content.replace('DQM_CLOUDSQL_DATABASE: "dqm"', f'DQM_CLOUDSQL_DATABASE: "{sql_db_name}"')

  with open('dqm/backend/app.yaml', 'w') as f:
    f.write(content)

  print(text_color('Deploying to App Engine app...', Color.BLUE))
  subprocess.check_output(['gcloud', 'app', 'deploy'], cwd='dqm/backend')

  print(text_color('All good, thanks for using DQM :)', Color.GREEN))

