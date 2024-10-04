# PIPES API

PIPES API built with FastAPI, DocDB &amp; Neptune.


**Prerequisites**:

* Docker - https://www.docker.com/get-started
* Docker Compose - https://docs.docker.com/compose/install/


## Development Environment

### 1. Docker Compose

**Create `.mongo` and `.env`**

```bash
$ cd pipes-api
$ mkdir .mongo
$ touch .env
```

In `.env` file,

```
# Environment
PIPES_ENV=local

# MongoDB
PIPES_DOCDB_HOST=mongodb
PIPES_DOCDB_PORT=27017
PIPES_DOCDB_NAME=pipes_dev
PIPES_DOCDB_USER=pipes
PIPES_DOCDB_PASS=

# Neptune
PIPES_NEPTUNE_HOST=
PIPES_NEPTUNE_PORT=8182
PIPES_NEPTUNE_SECURE=True

# Cognito
PIPES_REGION=us-west-2
PIPES_COGNITO_USER_POOL_ID=
PIPES_COGNITO_CLIENT_ID=
PIPES_COGNITO_USERNAME=
PIPES_COGNITO_PASSWORD=
```

**Build Images**

```bash
$ docker compose build
```

**Run Containers**

```bash
$ docker compose up
```

Then visit [http://127.0.0.1:8080](http://127.0.0.1:8080)


### 2. Pre-Commit

Create a Python virtual environment on your machine, and activate it. Then install Python packages for

```bash
$ pip install -r requirements-dev.txt
```

Then run

```bash
$ pre-commit install
```

`pre-commit` detects code problems before they enter the version control system. If any issue when committing, please
fix them, then add and commit again.

### 3. Automated Testing

Use `tox` to run tests,

```bash
$ tox
```

## Cognito Authentication

AWS Cognito has been integrated to authenticate access. Steps:

* Make sure your cognito username and password are configured in `.env`.
* Run `python scripts/get_cognito_access_token.py` to get the access token.
* Authenticate the Swagger Docs with the token for running API tests.

The access token would last for 12 hour before it expires.
After the expiration, you will need to re-run the script to get a new one.

Besides, you'll be granted as superuser at local for development.


## API Documentation

API documentation:  [http://localhost:8080/docs](http://localhost:8080/docs)
