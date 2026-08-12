"""
Django settings for staging environment.
Shop Template - Django E-commerce Template
Inherits from production settings with staging-specific overrides.
"""

from .production import *

# ============================================
# Staging-specific Settings
# ============================================

# Debug mode (False for staging, but can be True for debugging)
DEBUG = False

# Allowed hosts for staging
ALLOWED_HOSTS = get_env_var('ALLOWED_HOSTS', 'staging.shoptemplate.com,localhost,127.0.0.1').split(',')

# Internal IPs for debug toolbar
INTERNAL_IPS = get_env_var('INTERNAL_IPS', '127.0.0.1').split(',')

# ============================================
# Database (can use SQLite for staging if needed)
# ============================================

# Override database settings if needed
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# ============================================
# Cache Settings (use locmem for staging if Redis not available)
# ============================================

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake',
#     }
# }

# ============================================
# Email Settings (use console backend for staging)
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============================================
# Security Settings (less strict for staging)
# ============================================

# HTTPS settings (can be disabled for staging without HTTPS)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# ============================================
# Logging Settings (more verbose for staging)
# ============================================

LOG_LEVEL = get_env_var('LOG_LEVEL', 'DEBUG')

LOGGING['loggers']['django']['level'] = LOG_LEVEL
LOGGING['loggers']['']['level'] = LOG_LEVEL

# ============================================
# Celery Settings (can use locmem for staging)
# ============================================

# CELERY_BROKER_URL = 'redis://localhost:6379/1'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'

# Or use locmem for testing
# CELERY_BROKER_URL = 'memory://'
# CELERY_RESULT_BACKEND = 'cache+memory://'

# ============================================
# Feature Flags (can enable/disable for testing)
# ============================================

# Enable all features for staging
PRODUCT_REVIEWS_ENABLED = True
PRODUCT_REVIEWS_APPROVAL = False  # Auto-approve for staging
PRODUCT_RATINGS_ENABLED = True
WISHLIST_ENABLED = True
COMPARE_ENABLED = True
NEWSLETTER_ENABLED = True
SOCIAL_LOGIN_ENABLED = True
TWO_FACTOR_AUTH_ENABLED = True  # Test 2FA in staging
RECAPTCHA_ENABLED = False
MAINTENANCE_MODE = False

# ============================================
# Analytics Settings (disable for staging)
# ============================================

ANALYTICS_ENABLED = False

# ============================================
# Site Settings (staging-specific)
# ============================================

SITE_NAME = get_env_var('SITE_NAME', 'Shop Template - Staging')
SITE_DOMAIN = get_env_var('SITE_DOMAIN', 'staging.shoptemplate.com')

# ============================================
# Import local settings (if exists)
# ============================================

try:
    from .local import *
except ImportError:
    pass
