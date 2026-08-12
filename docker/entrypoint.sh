#!/bin/bash
# ============================================
# Docker Entrypoint Script
# Shop Template - Django E-commerce Template
# ============================================

set -e

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Determine the service to run
SERVICE=${1:-web}

case "$SERVICE" in
    web)
        echo "Starting web service..."
        exec /docker/web/start.sh
        ;;
    celery)
        echo "Starting Celery worker..."
        exec /docker/celery/worker/start.sh
        ;;
    celery-beat)
        echo "Starting Celery beat..."
        exec /docker/celery/beat/start.sh
        ;;
    *)
        echo "Unknown service: $SERVICE"
        echo "Available services: web, celery, celery-beat"
        exit 1
        ;;
esac
