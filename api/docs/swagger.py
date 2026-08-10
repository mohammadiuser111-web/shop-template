"""
Swagger/OpenAPI Configuration
"""

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny


schema_view = get_schema_view(
    openapi.Info(
        title="Shop Template API",
        default_version='v1',
        description="Complete e-commerce API for Shop Template",
        terms_of_service="https://github.com/mohammadiuser111-web/shop-template",
        contact=openapi.Contact(email="contact@shoptemplate.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)


def get_swagger_view():
    """
    Get Swagger UI view
    """
    return schema_view


# Schema generators for different modules
def get_core_schemas():
    """
    Get schemas for core module
    """
    return {
        'SiteSettings': {
            'type': 'object',
            'properties': {
                'site_name': {'type': 'string'},
                'site_description': {'type': 'string'},
                'logo': {'type': 'string', 'format': 'uri'},
                'favicon': {'type': 'string', 'format': 'uri'},
                'contact_email': {'type': 'string', 'format': 'email'},
                'contact_phone': {'type': 'string'},
                'address': {'type': 'string'},
                'currency': {'type': 'string'},
                'timezone': {'type': 'string'},
                'maintenance_mode': {'type': 'boolean'},
            }
        },
        'Country': {
            'type': 'object',
            'properties': {
                'code': {'type': 'string'},
                'name': {'type': 'string'},
                'phone_code': {'type': 'string'},
                'is_active': {'type': 'boolean'},
            }
        },
        'Currency': {
            'type': 'object',
            'properties': {
                'code': {'type': 'string'},
                'name': {'type': 'string'},
                'symbol': {'type': 'string'},
                'is_active': {'type': 'boolean'},
            }
        }
    }
