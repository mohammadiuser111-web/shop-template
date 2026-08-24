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
        exec /app/docker/web/start.sh
        ;;
    celery)
        echo "Starting Celery worker..."
        exec /app/docker/celery/worker/start.sh
        ;;
    celery-beat)
        echo "Starting Celery beat..."
        exec /app/docker/celery/beat/start.sh
        ;;
    *)
        echo "Unknown service: $SERVICE"
        echo "Available services: web, celery, celery-beat"
        exit 1
        ;;
esac
