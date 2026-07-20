#!/bin/sh
set -e

echo "Running database migrations..."
uv run --no-dev flask db upgrade

echo "Starting application..."
exec uv run --no-dev gunicorn --bind 0.0.0.0:8001 wsgi:app