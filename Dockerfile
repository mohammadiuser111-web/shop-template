# ============================================
# Dockerfile for Shop Template
# Multi-stage build with inline scripts in /opt/docker
# ============================================

# ============================================
# Stage 1: Builder stage (for production)
# ============================================
FROM --platform=linux/amd64 python:3.11-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple

# Install system dependencies - USTC mirror for Debian
RUN echo "deb https://mirrors.ustc.edu.cn/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    libpq-dev \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=300 -r requirements.txt

# Create virtual environment and install dependencies
RUN python -m venv /app/.venv
RUN /app/.venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir --default-timeout=300 -r requirements.txt

# ============================================
# Stage 2: Production stage
# ============================================
FROM --platform=linux/amd64 python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple

# Install system dependencies - USTC mirror for Debian
RUN echo "deb https://mirrors.ustc.edu.cn/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends --fix-missing \
    libpq5 \
    postgresql-client \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

# Copy project files
COPY . .

# Create directories
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/tmp

# Set permissions
RUN chmod -R 755 /app && \
    chown -R www-data:www-data /app/staticfiles /app/media /app/logs /app/tmp

# Create docker scripts directory in /opt/docker
RUN mkdir -p /opt/docker/web /opt/docker/celery/worker /opt/docker/celery/beat

# Create entrypoint.sh in /opt/docker
RUN cat << 'EOF' > /opt/docker/entrypoint.sh
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
EOF

RUN chmod +x /opt/docker/entrypoint.sh

# Create web/start.sh in /opt/docker
RUN cat << 'EOF' > /opt/docker/web/start.sh
#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=shop_template.settings.production
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

if [ -f "/app/.venv/bin/activate" ]; then
    source /app/.venv/bin/activate
fi

cd /app

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do sleep 1; done
echo "PostgreSQL is up!"

echo "Waiting for Redis..."
while ! nc -z redis 6379; do sleep 1; done
echo "Redis is up!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

if python -c "import compressor" 2>/dev/null; then
    echo "Compressing static files..."
    python manage.py compress --force
fi

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 300 --graceful-timeout 30 --keepalive 2 shop_template.wsgi:application
EOF

RUN chmod +x /opt/docker/web/start.sh

# Create celery/worker/start.sh in /opt/docker
RUN cat << 'EOF' > /opt/docker/celery/worker/start.sh
#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=shop_template.settings.production
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

if [ -f "/app/.venv/bin/activate" ]; then
    source /app/.venv/bin/activate
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
EOF

RUN chmod +x /opt/docker/celery/worker/start.sh

# Create celery/beat/start.sh in /opt/docker
RUN cat << 'EOF' > /opt/docker/celery/beat/start.sh
#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=shop_template.settings.production
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

if [ -f "/app/.venv/bin/activate" ]; then
    source /app/.venv/bin/activate
fi

cd /app

echo "Waiting for Redis..."
while ! nc -z redis 6379; do sleep 1; done
echo "Redis is up!"

echo "Starting Celery beat..."
exec celery -A shop_template beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
EOF

RUN chmod +x /opt/docker/celery/beat/start.sh

# Set entrypoint
ENTRYPOINT ["/opt/docker/entrypoint.sh"]
CMD ["web"]

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python /app/scripts/wait_for_db.py --timeout=5 || exit 1

# ============================================
# Stage 3: Development stage (optional)
# ============================================
FROM --platform=linux/amd64 python:3.11-slim-bookworm AS development

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBUG=1 \
    DJANGO_SETTINGS_MODULE=shop_template.settings.development \
    PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple

# Install system dependencies - USTC mirror for Debian
RUN echo "deb https://mirrors.ustc.edu.cn/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    libpq-dev \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Create virtual environment and install all dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=300 -r requirements.txt

# Create directories
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/tmp

# Create docker scripts directory in /opt/docker
RUN mkdir -p /opt/docker/web /opt/docker/celery/worker /opt/docker/celery/beat

# Create entrypoint.sh in /opt/docker
RUN cat << 'EOF' > /opt/docker/entrypoint.sh
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
EOF

RUN chmod +x /opt/docker/entrypoint.sh

# Create web/start.sh in /opt/docker
RUN cat << 'EOF' > /opt/docker/web/start.sh
#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=shop_template.settings.development
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

if [ -f "/opt/venv/bin/activate" ]; then
    source /opt/venv/bin/activate
fi

cd /app

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do sleep 1; done
echo "PostgreSQL is up!"

echo "Waiting for Redis..."
while ! nc -z redis 6379; do sleep 1; done
echo "Redis is up!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

if python -c "import compressor" 2>/dev/null; then
    echo "Compressing static files..."
    python manage.py compress --force
fi

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 300 --graceful-timeout 30 --keepalive 2 shop_template.wsgi:application
EOF

RUN chmod +x /opt/docker/web/start.sh

# Create celery/worker/start.sh in /opt/docker
RUN cat << 'EOF' > /opt/docker/celery/worker/start.sh
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
EOF

RUN chmod +x /opt/docker/celery/worker/start.sh

# Create celery/beat/start.sh in /opt/docker
RUN cat << 'EOF' > /opt/docker/celery/beat/start.sh
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
EOF

RUN chmod +x /opt/docker/celery/beat/start.sh

# Set entrypoint
ENTRYPOINT ["/opt/docker/entrypoint.sh"]
CMD ["web"]

# Expose port
EXPOSE 8000
