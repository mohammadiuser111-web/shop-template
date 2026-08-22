# ============================================
# Dockerfile for Shop Template
# Multi-stage build for production and development
# ============================================

# ============================================
# Stage 1: Build stage (for production)
# ============================================
FROM --platform=linux/amd64 python:3.11-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# Install system dependencies
# Use USTC mirror for Debian (works in Iran/China)
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

# Install system dependencies
# Use USTC mirror for Debian (works in Iran/China)
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

# Collect static files (will be done at runtime)
# RUN python manage.py collectstatic --noinput

# Set permissions
RUN chmod -R 755 /app && \
    chown -R www-data:www-data /app/staticfiles /app/media /app/logs /app/tmp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python /app/scripts/wait_for_db.py --timeout=5 || exit 1

# Set entrypoint to directly run start scripts
COPY docker/web/start.sh /app/docker/web/start.sh
COPY docker/celery/worker/start.sh /app/docker/celery/worker/start.sh
COPY docker/celery/beat/start.sh /app/docker/celery/beat/start.sh
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh /app/docker/web/start.sh /app/docker/celery/worker/start.sh /app/docker/celery/beat/start.sh

# Set entrypoint
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["web"]

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

# Install system dependencies
# Use USTC mirror for Debian (works in Iran/China)
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

# Create virtual environment and install all dependencies (including dev)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=300 -r requirements.txt

# Create directories
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/tmp

# Copy and set permissions for entrypoint and start scripts
COPY docker/web/start.sh /app/docker/web/start.sh
COPY docker/celery/worker/start.sh /app/docker/celery/worker/start.sh
COPY docker/celery/beat/start.sh /app/docker/celery/beat/start.sh
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh /app/docker/web/start.sh /app/docker/celery/worker/start.sh /app/docker/celery/beat/start.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["web"]
