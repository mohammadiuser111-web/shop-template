"""
ASGI configuration for Shop Template project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_template.settings')
django.setup()

# Get Django ASGI application
application = get_asgi_application()

# Import routing only if channels is installed
try:
    from shop_template import routing
    
    # Application definition for WebSocket support
    application = ProtocolTypeRouter({
        "http": application,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        ),
    })
except ImportError:
    # If routing.py doesn't exist, just use HTTP
    pass
