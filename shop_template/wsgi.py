"""
WSGI config for Shop Template project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# ============================================
# Add the project directory to the Python path
# ============================================

# Get the directory where this file is located
project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_template.settings')

# ============================================
# Application
# ============================================

application = get_wsgi_application()

# ============================================
# Application wrapper for better error handling
# ============================================

# def application(environ, start_response):
#     """WSGI application wrapper"""
#     try:
#         return _application(environ, start_response)
#     except Exception as e:
#         # Log the error
#         import logging
#         logger = logging.getLogger('django.wsgi')
#         logger.exception('WSGI application error')
#         
#         # Return a 500 error
#         status = '500 Internal Server Error'
#         response_body = b'Internal Server Error'
#         response_headers = [('Content-Type', 'text/plain')]
#         start_response(status, response_headers)
#         return [response_body]
# 
# _application = get_wsgi_application()

# ============================================
# Health check endpoint
# ============================================

# def health_check(environ, start_response):
#     """Health check endpoint for monitoring"""
#     if environ.get('PATH_INFO') == '/health/':
#         status = '200 OK'
#         response_body = b'OK'
#         response_headers = [('Content-Type', 'text/plain')]
#         start_response(status, response_headers)
#         return [response_body]
#     return application(environ, start_response)
# 
# application = health_check

# ============================================
# Export for use in other modules
# ============================================

__all__ = ['application']
