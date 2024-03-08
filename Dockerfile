FROM python:3.12-slim-bookworm

# set environment variables
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONUNBUFFERED=TRUE

# install system dependencies
RUN apt-get update -y --fix-missing && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoclean

# install python packages
WORKDIR /app
COPY ./requirements.txt requirements.txt
COPY ./requirements-dev.txt requirements-dev.txt
RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r requirements-dev.txt

# operations
COPY ./wait-for-mongodb.sh /wait-for-mongodb.sh
RUN chmod +x /wait-for-mongodb.sh
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# all code
COPY . .
