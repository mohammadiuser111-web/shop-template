#!/bin/bash
set -e

export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

SERVICE=${1:-web}

case "$SERVICE" in
    web)
        echo "Starting web service..."
        exec /opt/docker/web/start.sh
        ;;
    celery)
        echo "Starting Celery worker..."
        exec /opt/docker/celery/worker/start.sh
        ;;
    celery-beat)
        echo "Starting Celery beat..."
        exec /opt/docker/celery/beat/start.sh
        ;;
    *)
        echo "Unknown service: $SERVICE"
        echo "Available services: web, celery, celery-beat"
        exit 1
        ;;
esac
