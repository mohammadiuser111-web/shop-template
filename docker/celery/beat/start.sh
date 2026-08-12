#!/bin/bash
# ============================================
# Celery Beat Start Script
# Shop Template - Django E-commerce Template
# ============================================

set -e

# Set environment variables
export DJANGO_SETTINGS_MODULE=shop_template.settings.production
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Activate virtual environment (if exists)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Change to app directory
cd /app

# Wait for dependencies
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
    sleep 1
done
echo "Redis is up!"

# Run Celery beat
echo "Starting Celery beat..."
exec celery -A shop_template beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
