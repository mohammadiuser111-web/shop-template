# ============================================
# Gunicorn Configuration for Shop Template
# ============================================

import multiprocessing
import os
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Bind address
bind = "0.0.0.0:8000"

# Workers
# Use (2 * CPU cores + 1) as a general rule
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
# Use gevent for async workers (requires gevent package)
# worker_class = "gevent"
# Or use sync workers
worker_class = "gthread"

# Threads (only used with gthread worker class)
threads = 2

# Worker connections
worker_connections = 1000

# Maximum requests per worker before restart
max_requests = 1000
max_requests_jitter = 50

# Timeout
timeout = 300
graceful_timeout = 30
keepalive = 2

# Server sockets
backlog = 2048

# Debug
reload = os.getenv("DEBUG", "False").lower() == "true"

# SSL (if needed)
# keyfile = str(BASE_DIR / "ssl" / "private.key")
# certfile = str(BASE_DIR / "ssl" / "certificate.crt")

# Security
limit_request_fields = 32000
limit_request_field_size = 0  # Unlimited

# Environment
raw_env = [
    "DJANGO_SETTINGS_MODULE=shop_template.settings.production",
    "PYTHONUNBUFFERED=1",
    "PYTHONDONTWRITEBYTECODE=1",
]

# Logging
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Process naming
proc_name = "shop-template"

# Preload
preload_app = True

# Sendfile
sendfile = True

# Chdir
chdir = str(BASE_DIR)

# User and group
# user = "www-data"
# group = "www-data"

# Umask
umask = 0o022

# Tmp upload dir
tmp_upload_dir = None

# Statsd
# statsd_host = "localhost:8125"
# statsd_prefix = "shop-template"

# Dogstatsd
# dogstatsd_host = "localhost:8125"
# dogstatsd_tags = {"app": "shop-template"}
