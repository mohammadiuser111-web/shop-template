"""
Django settings for testing environment.
Shop Template - Django E-commerce Template
Used for running tests.
"""

import os
import sys
import tempfile
from pathlib import Path

# ============================================
# Path Configuration
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent

# Add project directory to path
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(PROJECT_DIR / 'apps'))

# ============================================
# Secret Key
# ============================================

SECRET_KEY = 'test-secret-key-for-testing-only'

# ============================================
# Debug Settings
# ============================================

DEBUG = True

# ============================================
# Allowed Hosts
# ============================================

ALLOWED_HOSTS = ['*']

# ============================================
# Installed Apps
# ============================================

INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_spectacular',
    'crispy_forms',
    'crispy_bootstrap5',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Local apps
    'apps.core',
    'apps.accounts',
    'apps.products',
    'apps.blog',
    'apps.orders',
    'apps.payments',
    'apps.shipping',
    'apps.ads',
    'apps.reviews',
    'apps.cart',
    'apps.discounts',
    'apps.notifications',
    'apps.dashboard_admin',
    'apps.inventory',
    'apps.support',
    'apps.dashboard',
]

# ============================================
# Middleware
# ============================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# ============================================
# Database Settings
# ============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': True,
    }
}

# ============================================
# Default Primary Key - Use BigAutoField for SQLite compatibility
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# URL Configuration
# ============================================

ROOT_URLCONF = 'shop_template.urls'

# ============================================
# WSGI Application
# ============================================

WSGI_APPLICATION = 'shop_template.wsgi.application'
ASGI_APPLICATION = 'shop_template.asgi.application'

# ============================================
# Template Settings
# ============================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================
# Password Hashers (fast for testing)
# ============================================

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# ============================================
# Email Backend (no emails during tests)
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ============================================
# File Storage (use temp directory for tests)
# ============================================

MEDIA_ROOT = tempfile.mkdtemp()
MEDIA_URL = '/media/'
STATIC_ROOT = tempfile.mkdtemp()
STATIC_URL = '/static/'

# ============================================
# Cache Backend (use locmem for tests)
# ============================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ============================================
# Internationalization
# ============================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================
# Sites Framework
# ============================================

SITE_ID = 1

# ============================================
# Security Settings (disable for testing)
# ============================================

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# ============================================
# Logging Settings (minimal for tests)
# ============================================

LOG_LEVEL = 'ERROR'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# ============================================
# Feature Flags (enable all for testing)
# ============================================

PRODUCT_REVIEWS_ENABLED = True
PRODUCT_REVIEWS_APPROVAL = False  # Auto-approve for tests
PRODUCT_RATINGS_ENABLED = True
WISHLIST_ENABLED = True
COMPARE_ENABLED = True
NEWSLETTER_ENABLED = True
SOCIAL_LOGIN_ENABLED = True
TWO_FACTOR_AUTH_ENABLED = True
RECAPTCHA_ENABLED = False
MAINTENANCE_MODE = False

# ============================================
# Test Runner
# ============================================

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# ============================================
# Default Primary Key
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# Auth Settings
# ============================================

AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ============================================
# Site Settings
# ============================================

SITE_NAME = 'Shop Template'
SITE_DESCRIPTION = 'Professional Django E-commerce Template'
SITE_KEYWORDS = 'ecommerce, django, shop, template'
SITE_AUTHOR = 'Shop Template Team'

# ============================================
# Theme Settings
# ============================================

THEME_DEFAULT = 'default'
THEMES = [
    {'name': 'default', 'title': 'Default Theme'},
    {'name': 'dark', 'title': 'Dark Theme'},
    {'name': 'light', 'title': 'Light Theme'},
]

# ============================================
# API Settings
# ============================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ============================================
# Spectacular API Docs
# ============================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Shop Template API',
    'DESCRIPTION': 'API documentation for Shop Template',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ============================================
# Celery Settings (use always_eager for tests)
# ============================================

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# ============================================
# Factory Boy Configuration
# ============================================

FACTORY_BOY_ALLOW_SAVE_WITHOUT_SESSION = True

# ============================================
# CORS Settings
# ============================================

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ============================================
# Allauth Settings
# ============================================

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# ============================================
# Crispy Forms
# ============================================

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
