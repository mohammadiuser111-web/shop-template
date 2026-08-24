#!/bin/bash
# ============================================
# Web Server Start Script
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
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
    sleep 1
done
echo "PostgreSQL is up!"

echo "Waiting for Redis..."
while ! nc -z redis 6379; do
    sleep 1
done
echo "Redis is up!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Compress static files (if django-compressor is installed)
if python -c "import compressor" 2>/dev/null; then
    echo "Compressing static files..."
    python manage.py compress --force
fi

# Create superuser (if needed)
# Uncomment and modify the following lines to create a superuser
# echo "Creating superuser..."
# python manage.py createsuperuser --noinput --username admin --email admin@example.com

# Run Gunicorn
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 300 --graceful-timeout 30 --keepalive 2 shop_template.wsgi:application
