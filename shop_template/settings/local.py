"""
Local settings for Shop Template.

This file contains settings that should NOT be committed to version control.
Copy this file from local.py.example and customize it for your local development.
"""

# ============================================
# Database Settings
# ============================================

# Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================
# Secret Key
# ============================================

# Generate a new secret key for local development
from django.core.management.utils import get_random_secret_key
SECRET_KEY = get_random_secret_key()

# ============================================
# Debug Settings
# ============================================

# Enable debug mode for local development
DEBUG = True

# Allow all hosts for local development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ============================================
# Email Settings (Console for local development)
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============================================
# Cache Settings (LocMem for local development)
# ============================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ============================================
# Static Files (for local development)
# ============================================

# Use local static files (not CDN)
STATIC_URL = '/static/'

# ============================================
# Media Files (for local development)
# ============================================

# Use local media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================
# Logging (for local development)
# ============================================

LOG_LEVEL = 'DEBUG'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

# ============================================
# Feature Flags (for local development)
# ============================================

# Enable all features for local development
PRODUCT_REVIEWS_ENABLED = True
PRODUCT_REVIEWS_APPROVAL = False
PRODUCT_RATINGS_ENABLED = True
WISHLIST_ENABLED = True
COMPARE_ENABLED = True
NEWSLETTER_ENABLED = True
SOCIAL_LOGIN_ENABLED = True
TWO_FACTOR_AUTH_ENABLED = False
RECAPTCHA_ENABLED = False
MAINTENANCE_MODE = False

# ============================================
# Custom Settings (for local development)
# ============================================

# Use local timezone for development
TIME_ZONE = 'Asia/Tehran'
