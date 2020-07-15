# DQM - Data Quality Manager

__Please note: this is not an officially supported Google product.__

Data Quality Manager (aka _DQM_) is a platform dedicated to data quality issues detection, especially in the context of online advertising.


## Automated deployment on GCP

A typical DQM deployment relies on [Google Cloud Platform](https://cloud.google.com/gcp/) (GCP) [App Engine](https://cloud.google.com/appengine/).

All you need is to [create a GCP project](https://cloud.google.com/resource-manager/docs/creating-managing-projects), and copy/paste the following command in the Cloud Shell console:

```shell
wget -qO dqm.py https://raw.githubusercontent.com/google/dqm/master/installer.py && python3 dqm.py
```

You will be prompted when needed during the process.


## Architecture

DQM is made of two components:

- A __backend__ (Python, Django) to execute/store checks.
- A __frontend__ (Typescript, VueJS) to allow users to plan/execute/monitor checks.


## Local installation

### Prerequisites

- A GCP project.
- The [Google Cloud SDK](https://cloud.google.com/sdk/docs) (command line interface) installed on your local machine.
- The [pipenv](https://github.com/pypa/pipenv) Python package manager installed on your local machine.
- The Node.js [npm](https://www.npmjs.com/get-npm) installed on your local machine.

### Getting the code

Clone this repository:

```
git clone https://github.com/google/dqm.git
```

### Building the frontend

```shell
cd dqm/frontend
npm install
npm run build
```

_Note_ – DQM is configured to export the build to `backend/www` (because the frontend build is intended to ship together with the backend to App Engine, where it will be served "statically").


### GCP project setup

Activate required APIs, setup database, create App Engine app and get your service account key file by executing the following commands (replace `[YOUR GCP PROJECT ID]` by your actual project ID):

```shell
cd ../backend
export gcpproject="[YOUR GCP PROJECT ID]"

gcloud config set project $gcpproject
gcloud services enable analytics.googleapis.com
gcloud services enable analyticsreporting.googleapis.com
gcloud sql instances create dqm --region="europe-west1"
gcloud sql databases create dqm --instance=dqm
gcloud sql users create dqmuser --instance=dqm
gcloud app create
gcloud iam service-accounts keys create ./key.json \
  --iam-account $gcpproject@appspot.gserviceaccount.com
```

_Note_ – Of course, you can change values/names in the lines above, but keep in mind that the `key.json` file will have to be deployed to App Engine, so it __must__ stay inside the `backend` dir anyway.

### Database setup

Because App Engine won't be able to handle [Django database migrations](https://docs.djangoproject.com/en/3.0/topics/migrations/) (~ tables creation) on the production environment, you'll have to run these migrations from your local machine __before__ actually deploying.

#### Installing Python dependencies

First, get the required Python packages thanks to pipenv:

```shell
pipenv install --dev
```

#### Creating database tables

Set the following environment variables on your local machine:

```shell
export DQM_CLOUDSQL_CONNECTION_NAME="[YOUR CLOUD SQL CONNECTION NAME]"
export DQM_CLOUDSQL_DATABASE="dqm"
export DQM_CLOUDSQL_USER="dqmuser"
```

_Note_ – `DQM_CLOUDSQL_CONNECTION_NAME` value should be something like `[YOUR GCP PROJECT ID]:us-central1:dqm`. If you're not sure, open the [GCP console](https://console.cloud.google.com/), navigate to the SQL module and copy the value of the _Instance connection name_ field.

Then, install `cloud_sql_proxy` following [this procedure](https://cloud.google.com/sql/docs/mysql/connect-admin-proxy#install) (basically, download the binary and make it executable). Once installed, you can launch the `cloud_sql_proxy` daemon, which will route your local app database traffic to your production GCP SQL database.

```shell
./cloud_sql_proxy -instances="$DQM_CLOUDSQL_CONNECTION_NAME"=tcp:3306 &
```

Finally, let Django create the database tables and fields:

```shell
pipenv run python manage.py makemigrations
pipenv run python manage.py makemigrations dqm
pipenv run python manage.py migrate
```

### Deployment to App Engine

App Engine relies on the `app.yaml` file to configure your app's settings. Update the `env_variables` section with your values:

```yaml
#...
env_variables:
  CLOUDSQL_CONNECTION_NAME: "[YOUR CLOUD SQL CONNECTION NAME]"
  CLOUDSQL_USER: "dqmuser"
  CLOUDSQL_DATABASE: "dqm"
  DQM_SERVICE_ACCOUNT_FILE_PATH: "key.json"
```

You're now ready to deploy:

```shell
gcloud app deploy
gcloud app browse
gcloud app logs tail -s default
```

### Optional features

#### Access restriction (recommended)

DQM has no per-user access restriction, but you do so by enabling GCP [Identity-Aware Proxy (IAP)](https://cloud.google.com/iap/docs/app-engine-quickstart).


## Development

### Backend

Start backend server with:

```shell
cd dqm/backend
pipenv run python manage.py
```

If you install/update other Python libs, don't forget to refresh the `requirements.txt` file before deploying (App Engine won't read your `Pipfile` but the `requirements.txt` instead):

```shell
pipenv lock --requirements > requirements.txt
```

#### Testing

```shell
pipenv run python manage.py test dqm
```

### Frontend

Start frontend dev server with:

```shell
cd dqm/frontend
npm run serve
```

## Roadmap

- A bunch of new GA related checks to come...
- Planed & asynchronous checks execution.
- Alerting.
- Checking stuff on other Google Marketing Platform tools (DV360, GA360...), Google Ads.
