# ============================================
# Dockerfile for Shop Template
# Multi-stage build with physical script files
# Using reliable mirrors for better connectivity
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
    PIP_DEFAULT_TIMEOUT=300

# Install system dependencies - Using mirrors.kernel.org for better reliability
RUN echo "deb http://mirrors.kernel.org/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.kernel.org/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
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
    PYTHONUNBUFFERED=1

# Install system dependencies - Using mirrors.kernel.org for better reliability
RUN echo "deb http://mirrors.kernel.org/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.kernel.org/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends --fix-missing \
    libpq5 \
    postgresql-client \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy script files to /opt/docker/ BEFORE COPY . .
COPY docker/ /opt/docker/
RUN chmod -R +x /opt/docker/

# Copy project files AFTER scripts
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

COPY . .

# Create directories
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/tmp

# Set permissions
RUN chmod -R 755 /app && \
    chown -R www-data:www-data /app/staticfiles /app/media /app/logs /app/tmp

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
    DJANGO_SETTINGS_MODULE=shop_template.settings.development

# Install system dependencies - Using mirrors.kernel.org for better reliability
RUN echo "deb http://mirrors.kernel.org/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.kernel.org/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    libpq-dev \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy development script files to /opt/docker/ BEFORE COPY . .
COPY docker-dev/ /opt/docker/
RUN chmod -R +x /opt/docker/

# Now copy project files AFTER creating scripts
COPY . .

# Create virtual environment and install all dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=300 -r requirements.txt

# Create directories
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/tmp

# Set entrypoint
ENTRYPOINT ["/opt/docker/entrypoint.sh"]
CMD ["web"]

# Expose port
EXPOSE 8000
