#!/bin/bash

poetry run python manage.py migrate --no-input

echo "Starting Django server..."
exec "$@"