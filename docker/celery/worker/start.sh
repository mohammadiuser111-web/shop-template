#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=shop_template.settings.development
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

if [ -f "/opt/venv/bin/activate" ]; then
    source /opt/venv/bin/activate
fi

cd /app

echo "Waiting for Redis..."
while ! nc -z redis 6379; do sleep 1; done
echo "Redis is up!"

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do sleep 1; done
echo "PostgreSQL is up!"

echo "Starting Celery worker..."
exec celery -A shop_template worker -l info --concurrency=4 --max-tasks-per-child=1000 --max-memory-per-child=300000
