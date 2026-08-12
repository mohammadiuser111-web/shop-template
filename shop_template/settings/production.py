"""
Django settings for production environment.
Shop Template - Django E-commerce Template
"""

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# ============================================
# Build paths inside the project
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================================
# Environment Variables
# ============================================

def get_env_var(var_name, default=None):
    """Get environment variable or raise exception"""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)


# ============================================
# Core Settings
# ============================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = get_env_var('ALLOWED_HOSTS', '').split(',')

# Internal IPs (for debug toolbar in staging)
INTERNAL_IPS = get_env_var('INTERNAL_IPS', '127.0.0.1').split(',')

# ============================================
# Application definition
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
    'django_filters',
    'crispy_forms',
    'crispy_bootstrap5',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
    'import_export',
    'compressor',
    'django_celery_beat',
    'django_celery_results',
    'channels',
    
    # Custom apps
    'core',
    'users',
    'products',
    'store',
    'blog',
    'orders',
    'payments',
    'shipping',
    'advertising',
    'newsletter',
    'reviews',
    'wishlist',
    'compare',
    'coupons',
    'notifications',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'shop_template.urls'

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
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'core.context_processors.site_settings',
                'core.context_processors.theme_settings',
                'core.context_processors.cart_context',
                'core.context_processors.wishlist_context',
                'core.context_processors.compare_context',
            ],
            'libraries': {
                'staticfiles': 'django.templatetags.static',
            },
        },
    },
]

WSGI_APPLICATION = 'shop_template.wsgi.application'
ASGI_APPLICATION = 'shop_template.asgi.application'

# ============================================
# Database
# ============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_var('POSTGRES_DB', 'postgres'),
        'USER': get_env_var('POSTGRES_USER', 'postgres'),
        'PASSWORD': get_env_var('POSTGRES_PASSWORD', 'postgres'),
        'HOST': get_env_var('POSTGRES_HOST', 'db'),
        'PORT': get_env_var('POSTGRES_PORT', '5432'),
    }
}

# Database connection pooling
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 5,
}

# ============================================
# Password validation
# ============================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================
# Internationalization
# ============================================

LANGUAGE_CODE = get_env_var('DEFAULT_LANGUAGE', 'en')

TIME_ZONE = get_env_var('TIMEZONE', 'UTC')

USE_I18N = True

USE_TZ = True

# Languages
LANGUAGES = [
    ('en', 'English'),
    ('fa', 'Persian'),
    ('ar', 'Arabic'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('de', 'German'),
    ('tr', 'Turkish'),
]

# Locale paths
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ============================================
# Static files (CSS, JavaScript, Images)
# ============================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Static files storage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# ============================================
# Media files
# ============================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================
# Default primary key field type
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# Custom User Model
# ============================================

AUTH_USER_MODEL = 'users.User'

# ============================================
# Sites Framework
# ============================================

SITE_ID = 1
SITES = [
    {
        'id': 1,
        'name': get_env_var('SITE_NAME', 'Shop Template'),
        'domain': get_env_var('SITE_DOMAIN', 'localhost:8000'),
    }
]

# ============================================
# Authentication
# ============================================

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth settings
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/account/email/confirmed/'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/account/email/confirmed/'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/account/login/'
ACCOUNT_LOGIN_REDIRECT_URL = '/account/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/account/'
ACCOUNT_PASSWORD_RESET_REDIRECT_URL = '/account/password/reset/done/'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SESSION_COOKIE_AGE = 1209600  # 2 weeks

# Social account providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
    },
    'github': {
        'SCOPE': ['user:email'],
    },
}

# ============================================
# Django REST Framework
# ============================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/hour',
        'anon': '50/hour',
        'login': '5/minute',
        'register': '3/minute',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
}

# ============================================
# JWT Settings
# ============================================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ============================================
# Crispy Forms
# ============================================

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ============================================
# Django Compressor
# ============================================

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_OFFLINE_CONTEXT = {
    'STATIC_URL': STATIC_URL,
    'DEBUG': DEBUG,
}

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]

COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

# ============================================
# Celery Settings
# ============================================

CELERY_BROKER_URL = get_env_var('CELERY_BROKER_URL', 'redis://redis:6379/1')
CELERY_RESULT_BACKEND = get_env_var('CELERY_RESULT_BACKEND', 'redis://redis:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 3600  # 1 hour
CELERY_TASK_SOFT_TIME_LIMIT = 1800  # 30 minutes
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # 1 minute
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ============================================
# Cache Settings
# ============================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': get_env_var('REDIS_URL', 'redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 100},
        },
        'KEY_PREFIX': 'shop_template',
        'TIMEOUT': 3600,  # 1 hour
    }
}

# Cache timeout for different levels
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'shop_template'

# ============================================
# Security Settings
# ============================================

# HTTPS settings
SESSION_COOKIE_SECURE = int(get_env_var('SESSION_COOKIE_SECURE', '1'))
CSRF_COOKIE_SECURE = int(get_env_var('CSRF_COOKIE_SECURE', '1'))
SECURE_SSL_REDIRECT = int(get_env_var('SECURE_SSL_REDIRECT', '1'))
SECURE_HSTS_SECONDS = int(get_env_var('SECURE_HSTS_SECONDS', '31536000'))  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = int(get_env_var('SECURE_HSTS_INCLUDE_SUBDOMAINS', '1'))
SECURE_HSTS_PRELOAD = int(get_env_var('SECURE_HSTS_PRELOAD', '1'))
SECURE_CONTENT_TYPE_NOSNIFF = int(get_env_var('SECURE_CONTENT_TYPE_NOSNIFF', '1'))
SECURE_BROWSER_XSS_FILTER = int(get_env_var('SECURE_BROWSER_XSS_FILTER', '1'))
X_FRAME_OPTIONS = get_env_var('X_FRAME_OPTIONS', 'DENY')
REFERRER_POLICY = get_env_var('REFERRER_POLICY', 'same-origin')

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com")
CSP_IMG_SRC = ("'self'", "data:", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
CSP_FONT_SRC = ("'self'", "https://fonts.googleapis.com", "https://fonts.gstatic.com")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_SRC = ("'self'",)
CSP_OBJECT_SRC = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_REPORT_URI = None
CSP_REPORT_ONLY = False

# ============================================
# Session Settings
# ============================================

SESSION_COOKIE_AGE = int(get_env_var('SESSION_COOKIE_AGE', '1209600'))  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_SAVE_EVERY_REQUEST = False

# ============================================
# CSRF Settings
# ============================================

CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = get_env_var('CSRF_TRUSTED_ORIGINS', 'https://localhost,https://127.0.0.1').split(',')
CSRF_USE_SESSIONS = False

# ============================================
# Message Settings
# ============================================

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# ============================================
# File Upload Settings
# ============================================

FILE_UPLOAD_MAX_MEMORY_SIZE = int(get_env_var('FILE_UPLOAD_MAX_MEMORY_SIZE', '10')) * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_DISK_SIZE = int(get_env_var('FILE_UPLOAD_MAX_DISK_SIZE', '100')) * 1024 * 1024  # 100MB

DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# ============================================
# Media Settings
# ============================================

# File extensions
FILE_UPLOAD_ALLOWED_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt',
    '.mp4', '.mov', '.avi', '.webm',
]

# Image settings
IMAGE_QUALITY = 85
IMAGE_RESIZE_ENABLED = True
IMAGE_MAX_SIZE = (1920, 1080)
THUMBNAIL_SIZE = (300, 300)

# ============================================
# Pagination Settings
# ============================================

PAGINATOR_PAGE_RANGE = 5
PAGINATOR_MARGIN_PAGES = 2

# ============================================
# Site Settings
# ============================================

SITE_NAME = get_env_var('SITE_NAME', 'Shop Template')
SITE_DESCRIPTION = get_env_var('SITE_DESCRIPTION', 'A complete e-commerce solution built with Django')
SITE_KEYWORDS = get_env_var('SITE_KEYWORDS', 'e-commerce, django, shop, store, online shopping')
SITE_AUTHOR = get_env_var('SITE_AUTHOR', 'Shop Template Team')
SITE_EMAIL = get_env_var('SITE_EMAIL', 'info@shoptemplate.com')
SITE_PHONE = get_env_var('SITE_PHONE', '+1 234 567 890')
SITE_ADDRESS = get_env_var('SITE_ADDRESS', '123 Main Street, City, Country')
SITE_DOMAIN = get_env_var('SITE_DOMAIN', 'localhost:8000')

# ============================================
# Currency & Payment Settings
# ============================================

DEFAULT_CURRENCY = get_env_var('DEFAULT_CURRENCY', 'USD')
CURRENCY_SYMBOL = '$'
CURRENCY_POSITION = 'left'  # left, right, prefix, suffix
DECIMAL_SEPARATOR = '.'
THOUSAND_SEPARATOR = ','

# Payment gateways
STRIPE_PUBLIC_KEY = get_env_var('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = get_env_var('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = get_env_var('STRIPE_WEBHOOK_SECRET', '')

PAYPAL_CLIENT_ID = get_env_var('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = get_env_var('PAYPAL_CLIENT_SECRET', '')
PAYPAL_MODE = get_env_var('PAYPAL_MODE', 'sandbox')

# ============================================
# Shipping Settings
# ============================================

SHIPPING_FLAT_RATE_COST = float(get_env_var('SHIPPING_FLAT_RATE_COST', '5.00'))
SHIPPING_FLAT_RATE_NAME = get_env_var('SHIPPING_FLAT_RATE_NAME', 'Flat Rate')

SHIPPING_FREE_THRESHOLD = float(get_env_var('SHIPPING_FREE_THRESHOLD', '50.00'))
SHIPPING_FREE_NAME = get_env_var('SHIPPING_FREE_NAME', 'Free Shipping')

SHIPPING_LOCAL_PICKUP_COST = float(get_env_var('SHIPPING_LOCAL_PICKUP_COST', '0.00'))
SHIPPING_LOCAL_PICKUP_NAME = get_env_var('SHIPPING_LOCAL_PICKUP_NAME', 'Local Pickup')

# ============================================
# Tax Settings
# ============================================

TAX_RATE = float(get_env_var('TAX_RATE', '0.1'))  # 10%
TAX_INCLUDED_IN_PRICE = False

# ============================================
# Inventory Settings
# ============================================

LOW_STOCK_THRESHOLD = int(get_env_var('LOW_STOCK_THRESHOLD', '10'))
STOCK_CHECK_ENABLED = True

# ============================================
# Order Settings
# ============================================

MIN_ORDER_AMOUNT = float(get_env_var('MIN_ORDER_AMOUNT', '10.00'))
MAX_ORDER_AMOUNT = float(get_env_var('MAX_ORDER_AMOUNT', '10000.00'))
ORDER_EXPIRATION_TIME = int(get_env_var('ORDER_EXPIRATION_TIME', '24'))  # hours
ORDER_CONFIRMATION_EMAIL = True
ORDER_STATUS_UPDATE_EMAIL = True

# ============================================
# Email Settings
# ============================================

EMAIL_BACKEND = get_env_var('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = get_env_var('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(get_env_var('EMAIL_PORT', '587'))
EMAIL_USE_TLS = int(get_env_var('EMAIL_USE_TLS', '1'))
EMAIL_USE_SSL = int(get_env_var('EMAIL_USE_SSL', '0'))
EMAIL_HOST_USER = get_env_var('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = get_env_var('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = get_env_var('DEFAULT_FROM_EMAIL', 'noreply@shoptemplate.com')
REPLY_TO_EMAIL = get_env_var('REPLY_TO_EMAIL', 'info@shoptemplate.com')
SUPPORT_EMAIL = get_env_var('SUPPORT_EMAIL', 'support@shoptemplate.com')

# ============================================
# Newsletter Settings
# ============================================

NEWSLETTER_ENABLED = int(get_env_var('NEWSLETTER_ENABLED', '1'))
NEWSLETTER_CONFIRMATION_REQUIRED = True
NEWSLETTER_WELCOME_EMAIL = True

# ============================================
# Social Login Settings
# ============================================

SOCIAL_LOGIN_ENABLED = int(get_env_var('SOCIAL_LOGIN_ENABLED', '1'))
GOOGLE_CLIENT_ID = get_env_var('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = get_env_var('GOOGLE_CLIENT_SECRET', '')
FACEBOOK_APP_ID = get_env_var('FACEBOOK_APP_ID', '')
FACEBOOK_APP_SECRET = get_env_var('FACEBOOK_APP_SECRET', '')
GITHUB_CLIENT_ID = get_env_var('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = get_env_var('GITHUB_CLIENT_SECRET', '')

# ============================================
# Analytics Settings
# ============================================

ANALYTICS_ENABLED = int(get_env_var('ANALYTICS_ENABLED', '0'))
GOOGLE_ANALYTICS_ID = get_env_var('GOOGLE_ANALYTICS_ID', '')
GOOGLE_TAG_MANAGER_ID = get_env_var('GOOGLE_TAG_MANAGER_ID', '')
FACEBOOK_PIXEL_ID = get_env_var('FACEBOOK_PIXEL_ID', '')
HOTJAR_ID = get_env_var('HOTJAR_ID', '')

# ============================================
# Feature Flags
# ============================================

PRODUCT_REVIEWS_ENABLED = int(get_env_var('PRODUCT_REVIEWS_ENABLED', '1'))
PRODUCT_REVIEWS_APPROVAL = int(get_env_var('PRODUCT_REVIEWS_APPROVAL', '1'))
PRODUCT_RATINGS_ENABLED = int(get_env_var('PRODUCT_RATINGS_ENABLED', '1'))
WISHLIST_ENABLED = int(get_env_var('WISHLIST_ENABLED', '1'))
COMPARE_ENABLED = int(get_env_var('COMPARE_ENABLED', '1'))
NEWSLETTER_ENABLED = int(get_env_var('NEWSLETTER_ENABLED', '1'))
SOCIAL_LOGIN_ENABLED = int(get_env_var('SOCIAL_LOGIN_ENABLED', '1'))
TWO_FACTOR_AUTH_ENABLED = int(get_env_var('TWO_FACTOR_AUTH_ENABLED', '0'))
RECAPTCHA_ENABLED = int(get_env_var('RECAPTCHA_ENABLED', '0'))
MAINTENANCE_MODE = int(get_env_var('MAINTENANCE_MODE', '0'))

# Recaptcha settings
RECAPTCHA_PUBLIC_KEY = get_env_var('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = get_env_var('RECAPTCHA_PRIVATE_KEY', '')
RECAPTCHA_VERSION = 'v2'

# ============================================
# Logging Settings
# ============================================

LOG_LEVEL = get_env_var('LOG_LEVEL', 'INFO')
LOG_FILE = get_env_var('LOG_FILE', '/app/logs/django.log')

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
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django_errors.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

# ============================================
# Custom Settings
# ============================================

# Pagination
ITEMS_PER_PAGE = int(get_env_var('ITEMS_PER_PAGE', '12'))
BLOG_POSTS_PER_PAGE = int(get_env_var('BLOG_POSTS_PER_PAGE', '10'))

# API Settings
API_VERSION = 'v1'
API_PREFIX = '/api'

# Theme settings
THEME_NAME = 'default'
THEME_COLOR_SCHEME = 'light'  # light, dark, auto
THEME_DIRECTION = 'ltr'  # ltr, rtl

# ============================================
# Maintenance Mode
# ============================================

MAINTENANCE_MODE = int(get_env_var('MAINTENANCE_MODE', '0'))
MAINTENANCE_MESSAGE = 'We are currently undergoing maintenance. Please check back soon.'
MAINTENANCE_RETRY_AFTER = 3600  # 1 hour in seconds

# ============================================
# Import local settings (if exists)
# ============================================

try:
    from .local import *
except ImportError:
    pass
