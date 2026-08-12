"""
Django settings for development environment.
Shop Template - Django E-commerce Template
"""

from .base import *

# ============================================
# Debug Settings
# ============================================

DEBUG = True

# ============================================
# Database Settings
# ============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True,
    }
}

# ============================================
# Email Backend (console for development)
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

# ============================================
# Cache Backend (locmem for development)
# ============================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ============================================
# Celery Settings (local for development)
# ============================================

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# ============================================
# Security Settings (relaxed for development)
# ============================================

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# ============================================
# Logging Settings
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
            'formatter': 'verbose',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'development.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ============================================
# Django Debug Toolbar
# ============================================

INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

INTERNAL_IPS = ['127.0.0.1', 'localhost']

# ============================================
# Feature Flags (enable all for development)
# ============================================

PRODUCT_REVIEWS_ENABLED = True
PRODUCT_REVIEWS_APPROVAL = False
PRODUCT_RATINGS_ENABLED = True
WISHLIST_ENABLED = True
COMPARE_ENABLED = True
NEWSLETTER_ENABLED = True
SOCIAL_LOGIN_ENABLED = False
TWO_FACTOR_AUTH_ENABLED = False
RECAPTCHA_ENABLED = False
MAINTENANCE_MODE = False
