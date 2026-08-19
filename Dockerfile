# ============================================
# Dockerfile for Shop Template
# Multi-stage build for production and development
# ============================================

# ============================================
# Stage 1: Build stage (for production)
# ============================================
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY requirements.txt .

# Install dependencies in a virtual environment
RUN poetry config virtualenvs.in-project true && \
    poetry config experimental.new-installer false && \
    poetry install --no-dev --no-interaction --no-ansi

# ============================================
# Stage 2: Production stage
# ============================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/venv

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

# Set entrypoint
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["web"]

# ============================================
# Stage 3: Development stage (optional)
# ============================================
FROM python:3.11 as development

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBUG=1 \
    DJANGO_SETTINGS_MODULE=shop_template.settings.development

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/opt/poetry/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install all dependencies (including dev)
RUN poetry config virtualenvs.in-project true && \
    poetry config experimental.new-installer false && \
    poetry install --no-interaction --no-ansi

# Create directories
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/tmp

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["web"]
