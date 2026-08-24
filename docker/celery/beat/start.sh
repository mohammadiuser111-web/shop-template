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

echo "Starting Celery beat..."
exec celery -A shop_template beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
