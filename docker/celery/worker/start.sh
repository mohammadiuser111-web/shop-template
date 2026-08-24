#!/bin/bash
# ============================================
# Celery Worker Start Script
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

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
    sleep 1
done
echo "PostgreSQL is up!"

# Run Celery worker
echo "Starting Celery worker..."
exec celery -A shop_template worker -l info --concurrency=4 --max-tasks-per-child=1000 --max-memory-per-child=300000
