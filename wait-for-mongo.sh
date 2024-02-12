#!/usr/bin/env bash

echo "Waiting for MongoDB..."

while ! nc -z $MONGO_HOST $MONGO_PORT; do
  sleep 0.2
done

echo "MongoDB started!"

exec "$@"
