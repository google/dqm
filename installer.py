#!/usr/bin/env python3
from enum import Enum, auto
import time
import subprocess
import os
import sys
from shutil import rmtree
from datetime import datetime
from dataclasses import dataclass, asdict


class Color(Enum):
  HEADER = '\033[95m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  ORANGE = '\033[93m'
  RED = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


def color_text(text: str, color: Color = Color.BOLD, space_before: bool = True) -> str:
  return '{space}{color}{text}{end}'.format(space='\n' if space_before else '', color=color.value, text=text, end='\033[0m')

def abort() -> None:
  print(color_text('Deployment canceled.', Color.RED))
  sys.exit(0)

def set_project_id() -> str:
  project_set = False
  while not project_set:
    prompt = input(color_text('Enter the GCP project ID you want to deploy to? '))
    subprocess.check_output(['gcloud', 'config', 'set', 'project', prompt])
    current_project_id = subprocess.check_output(['gcloud', 'config', 'list', '--format', 'value(core.project)']).decode('utf-8').replace('\n','')
    if current_project_id == prompt:
        project_set = True
  return current_project_id

def get_project_id() -> str:
  current_project_id = subprocess.check_output(['gcloud', 'config', 'list', '--format', 'value(core.project)']).decode('utf-8').replace('\n','')
  prompt = input(color_text('DQM will be deployed within GCP project "{}", is that OK? (Y/n) '.format(current_project_id)))
  project_id = current_project_id if prompt.lower() != 'n' else set_project_id()
  print(color_text('DQM will be deployed within GCP project "{}".'.format(project_id), Color.BLUE))
  return project_id

def check_source_dir() -> None:
  if os.path.isdir('./dqm'):
    prompt = input(color_text('Existing "dqm" dir in current path should be deleted, proceed? ([Y]es/[s]kip) '))
    # if prompt.lower() == 'n':
      # abort()
    if prompt.lower() != 's':
      rmtree('./dqm')

def clone_repo() -> None:
  if input(color_text('Next step -> Download sources ([Y]es/[s]kip) ')).lower() != 's':
    subprocess.check_output(['git', 'clone', 'https://github.com/google/dqm.git'])

def clone_repo() -> None:
  if input(color_text('Next step -> Download sources ([Y]es/[s]kip) ')).lower() != 's':
    subprocess.check_output(['git', 'clone', 'https://github.com/google/dqm.git'])

def install_frontend_deps() -> None:
  if input(color_text('Next step -> Install frontend dependencies ([Y]es/[s]kip) ')).lower() != 's':
    subprocess.check_output(['npm', 'install'], cwd='dqm/frontend')

def build_frontend() -> None:
  if input(color_text('Next step -> Build frontend (it can take a little while...) ([Y]es/[s]kip) ')).lower() != 's':
    subprocess.check_output(['npm', 'run', 'build'], cwd='dqm/frontend')

def install_pipenv() -> None:
  if input(color_text('Next step -> Install pipenv ([Y]es/[s]kip) ')).lower() != 's':
    subprocess.check_output(['pip3', 'install', '--user', 'pipenv'])

def install_backend_deps() -> None:
  if input(color_text('Next step -> Install backend dependencies ([Y]es/[s]kip) ')).lower() != 's':
    subprocess.check_output(['python3', '-m', 'pipenv', 'install', '--dev'], cwd='dqm/backend')

def enable_apis() -> None:
  if input(color_text('Next step -> Enable APIs ([Y]es/[s]kip) ')).lower() != 's':
    subprocess.check_output(['gcloud', 'services', 'enable', 'analytics.googleapis.com'])
    subprocess.check_output(['gcloud', 'services', 'enable', 'analyticsreporting.googleapis.com'])

def create_gae_app() -> None:
  if input(color_text('Next step -> Create App Engine application ([Y]es/[s]kip) ')).lower() != 's':
    try:
      subprocess.check_output(['gcloud', 'app', 'create'])
    except subprocess.CalledProcessError as e:
      print(color_text('Failed to create App Engine app (this is normal if you have an existing app).', Color.ORANGE))
      prompt = input(color_text('Continue anyway and deploy on existing app? (Y/n) '))
      if prompt.lower() == 'n':
        abort()

def create_sa_keys() -> None:
  if input(color_text('Next step -> Download service account key file ([Y]es/[s]kip) ')).lower() != 's':
    subprocess.check_output(['gcloud', 'iam', 'service-accounts', 'keys', 'create', './key.json', '--iam-account', f'{project_id}@appspot.gserviceaccount.com'], cwd='dqm/backend')


def setup_database() -> (str, str, str):
  if input(color_text('Next step -> Database setup ([Y]es/[s]kip) ')).lower() == 's':
    return None, None, None
  else:
    prompt = input(color_text('Do you want to reuse an existing SQL instance? (y/N) ', Color.BOLD))
    create_sql_instance = True if prompt.lower() != 'y' else False
    sql_instance_name = input(color_text('SQL instance name (dqm)? ', Color.BOLD)) or 'dqm'
    sql_instance_region = input(color_text('SQL instance region (europe-west1)? ', Color.BOLD)) or 'europe-west1'
    if create_sql_instance:
      print(color_text('Creating SQL instance (it can take a little while)...', Color.BLUE))
      subprocess.check_output(['gcloud', 'sql', 'instances', 'create', sql_instance_name, '--region={}'.format(sql_instance_region)])

    prompt = input(color_text('Do you want to reuse an existing MySQL database? (y/N) ', Color.BOLD))
    create_sql_db = True if prompt.lower() != 'y' else False
    sql_db_name = input(color_text('MySQL database name (dqm)? ', Color.BOLD)) or 'dqm'
    if create_sql_db:
      print(color_text('Creating MySQL database...', Color.BLUE))
      subprocess.check_output(['gcloud', 'sql', 'databases', 'create', sql_db_name, '--instance={}'.format(sql_instance_name)])

    prompt = input(color_text('Do you want to reuse an existing MySQL user? (y/N) ', Color.BOLD))
    create_sql_user = True if prompt.lower() != 'y' else False
    sql_user_name = input(color_text('MySQL user name (dqmuser)? ', Color.BOLD)) or 'dqmuser'
    if create_sql_user:
      print(color_text('Creating MySQL user...', Color.BLUE))
      subprocess.check_output(['gcloud', 'sql', 'users', 'create', sql_user_name, '--instance={}'.format(sql_instance_name)])

    print(color_text('Connecting to database...', Color.BLUE))
    subprocess.check_output(['wget', 'https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64', '-O', 'cloud_sql_proxy'], cwd='dqm/backend')
    subprocess.check_output(['chmod', '+x', 'cloud_sql_proxy'], cwd='dqm/backend')
    connection_name = f'{project_id}:{sql_instance_region}:{sql_instance_name}'
    subprocess.Popen(['./cloud_sql_proxy', f'-instances={connection_name}=tcp:3306'], stdout=subprocess.PIPE, cwd='dqm/backend')

    # Wait for database connection to be available...
    time.sleep(4)

    prompt = input(color_text('Do you want to migrate database schema now? (Y/n) ', Color.BOLD))
    migrate_database = True if prompt.lower() != 'n' else False
    if migrate_database:
      print(color_text('Migrating database...', Color.BLUE))
      os.putenv('DQM_CLOUDSQL_CONNECTION_NAME', connection_name)
      os.putenv('DQM_CLOUDSQL_DATABASE', sql_db_name)
      os.putenv('DQM_CLOUDSQL_USER', sql_user_name)
      subprocess.check_output(['python3', '-m', 'pipenv', 'run', 'python', 'manage.py', 'makemigrations'], cwd='dqm/backend')
      subprocess.check_output(['python3', '-m', 'pipenv', 'run', 'python', 'manage.py', 'makemigrations', 'dqm'], cwd='dqm/backend')
      subprocess.check_output(['python3', '-m', 'pipenv', 'run', 'python', 'manage.py', 'migrate'], cwd='dqm/backend')

    return connection_name, sql_user_name, sql_db_name

def update_app_yaml(connection_name: str, sql_user_name: str, sql_db_name: str) -> None:
  if input(color_text('Next step -> Uupdate app.yaml file ([Y]es/[s]kip) ')).lower() != 's':
    with open('dqm/backend/app.yaml', 'r') as f:
      content = f.read()
      content = content.replace('DQM_CLOUDSQL_CONNECTION_NAME: ""', f'DQM_CLOUDSQL_CONNECTION_NAME: "{connection_name}"')
      content = content.replace('DQM_CLOUDSQL_USER: "dqmuser"', f'DQM_CLOUDSQL_USER: "{sql_user_name}"')
      content = content.replace('DQM_CLOUDSQL_DATABASE: "dqm"', f'DQM_CLOUDSQL_DATABASE: "{sql_db_name}"')
    with open('dqm/backend/app.yaml', 'w') as f:
      f.write(content)

def generate_requirements() -> None:
  if input(color_text('Next step -> Generate requirements.txt file ([Y]es/[s]kip) ')).lower() != 's':
    with open('dqm/backend/requirements.txt', 'w') as f:
      subprocess.call(['python3', '-m', 'pipenv', 'lock', '--requirements'], cwd='dqm/backend', stdout=f)

def deploy() -> None:
  if input(color_text('Next step -> Deploy to App Engine ([Y]es/[s]kip) ')).lower() != 's':
    subprocess.check_output(['gcloud', 'app', 'deploy'], cwd='dqm/backend')



if __name__ == '__main__':
  print(color_text('┌────────────────────────────────────────────────┐', Color.HEADER, space_before=False))
  print(color_text('│ Welcome to Data Quality Manager GCP installer! │', Color.HEADER, space_before=False))
  print(color_text('└────────────────────────────────────────────────┘', Color.HEADER, space_before=False))

  project_id = get_project_id()
  check_source_dir()
  clone_repo()
  install_frontend_deps()
  build_frontend()
  install_pipenv()
  install_backend_deps()
  enable_apis()
  create_gae_app()
  create_sa_keys()
  connection_name, sql_user_name, sql_db_name = setup_database()
  if all([connection_name, sql_user_name, sql_db_name]):
    update_app_yaml(connection_name, sql_user_name, sql_db_name)
  generate_requirements()
  deploy()

  print(color_text('All good, thanks for using DQM :)', Color.GREEN))
