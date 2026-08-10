# Dockerfile for shop-template project
# Multi-stage build for production and development

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
WORKDIR /app
COPY requirements/base.txt /app/
RUN pip install --no-cache-dir -r base.txt

# Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /app /static /media /logs /var/run/supervisor

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
WORKDIR /app
COPY . /app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash shopuser && \
    chown -R shopuser:shopuser /app /static /media /logs

# Switch to non-root user
USER shopuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose ports
EXPOSE 8000 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python /app/manage.py health_check || exit 1

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/app/docker/supervisord.conf"]
