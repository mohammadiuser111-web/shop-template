"""
API Settings
Configuration for the REST API
"""

from django.conf import settings


# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.auth.jwt_auth.CustomJWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'ALLOWED_VERSIONS': ['v1'],
    'VERSION_PARAM': 'version',
    'DEFAULT_VERSION': 'v1',
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'errors',
}


# JWT Settings
JWT_AUTH = {
    'JWT_SECRET_KEY': settings.SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_SIGNATURE': True,
    'JWT_EXPIRATION_DELTA': settings.TIME_ZONE,
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': settings.TIME_ZONE * 7,  # 7 days
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_AUTH_COOKIE': 'jwt_token',
    'JWT_AUTH_COOKIE_DOMAIN': None,
    'JWT_AUTH_COOKIE_PATH': '/',
    'JWT_AUTH_COOKIE_SAMESITE': 'Lax',
}


# API Rate Limiting
API_RATE_LIMITS = {
    'anonymous': '100/hour',
    'user': '1000/hour',
    'authenticated': '10000/hour',
}


# API Security
API_SECURITY = {
    'ENABLE_CSRF': True,
    'ENABLE_CORS': True,
    'ALLOWED_ORIGINS': [
        'http://localhost',
        'http://127.0.0.1',
        'https://shop-template.com',
    ],
    'ALLOWED_METHODS': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    'ALLOWED_HEADERS': ['*'],
    'ALLOW_CREDENTIALS': True,
}


# File Upload Settings
FILE_UPLOAD = {
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'MAX_IMAGE_SIZE': 5 * 1024 * 1024,  # 5MB
    'ALLOWED_IMAGE_TYPES': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'ALLOWED_FILE_TYPES': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'],
}


# Pagination Settings
PAGINATION = {
    'DEFAULT_PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'SMALL_PAGE_SIZE': 10,
    'LARGE_PAGE_SIZE': 50,
}


# Cache Settings
API_CACHE = {
    'ENABLE_CACHE': True,
    'CACHE_TIMEOUT': 300,  # 5 minutes
    'CACHE_PREFIX': 'api',
}


# Logging Settings
API_LOGGING = {
    'ENABLE_LOGGING': True,
    'LOG_LEVEL': 'INFO',
    'LOG_REQUESTS': True,
    'LOG_RESPONSES': False,
    'LOG_ERRORS': True,
}


# Email Settings for API notifications
API_EMAIL = {
    'FROM_EMAIL': 'noreply@shoptemplate.com',
    'ADMIN_EMAIL': 'admin@shoptemplate.com',
    'EMAIL_SUBJECT_PREFIX': '[Shop Template API]',
}
