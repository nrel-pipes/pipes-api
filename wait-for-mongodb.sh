#!/usr/bin/env bash

echo "Waiting for MongoDB..."

while ! nc -z $PIPES_DOCDB_HOST $PIPES_DOCDB_PORT; do
  sleep 0.2
done

echo "MongoDB started!"

exec "$@"
