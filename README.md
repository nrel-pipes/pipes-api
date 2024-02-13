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
# env
PIPES_ENVIRONMENT=local

# mongo
MONGO_HOST=mongo
MONGO_PORT=27017
```

**Build Images**

```bash
$ docker compose build
```

**Run Containers**

```bash
$ docker compose up
```

Visit [localhost:8080](http://localhost:8080) for local development.


### 2. Pre-Commit

Create a Python virtual environment on your machine, and activate it. Then install Python packages for

```bash
$ pip install -r requirements-dev.txt
```

`pre-commit` is installed, which would detect code problems before they enter the version control system.

### 3. Automated Testing

Use `tox` to run tests,

```bash
$ tox
```

## API Documentation

API documentation:  [http://localhost:8080/docs](http://localhost:8080/docs)
