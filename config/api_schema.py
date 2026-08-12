"""
OpenAPI Schema for Shop Template API
"""
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema
from rest_framework import serializers

# Custom schema for better API documentation
class CustomAutoSchema(AutoSchema):
    """Custom schema with improved documentation."""
    
    def get_endpoints(self, request=None):
        """Get all API endpoints with better organization."""
        endpoints = super().get_endpoints(request)
        
        # Group endpoints by app
        grouped_endpoints = {}
        for path, path_info in endpoints.items():
            # Extract app name from path
            path_parts = path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == 'api':
                if len(path_parts) >= 3 and path_parts[1] == 'v1':
                    app_name = path_parts[2] if path_parts[2] else 'root'
                else:
                    app_name = path_parts[1] if path_parts[1] else 'root'
            else:
                app_name = 'other'
            
            if app_name not in grouped_endpoints:
                grouped_endpoints[app_name] = {}
            grouped_endpoints[app_name][path] = path_info
        
        return grouped_endpoints


# API Info
API_INFO = {
    "title": "Shop Template API",
    "description": "Complete REST API for Shop Template e-commerce platform",
    "version": "1.0.0",
    "terms_of_service": "https://shop-template.com/terms/",
    "contact": {
        "name": "Shop Template Support",
        "email": "support@shop-template.com",
        "url": "https://shop-template.com/support/"
    },
    "license": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    "servers": [
        {
            "url": "http://localhost:8000/api/v1",
            "description": "Development server"
        },
        {
            "url": "https://api.shop-template.com/api/v1",
            "description": "Production server"
        }
    ]
}


# Security Schemes
SECURITY_SCHEMES = [
    {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "name": "JWT Authentication",
        "description": "Use JWT token for authentication. Get token from /api/v1/accounts/login/"
    },
    {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "description": "Token authentication (for legacy clients)"
    },
    {
        "type": "cookie",
        "name": "sessionid",
        "description": "Session cookie for web-based authentication"
    }
]


# Tags for organizing endpoints
API_TAGS = [
    {
        "name": "Authentication",
        "description": "User authentication and authorization endpoints"
    },
    {
        "name": "Users",
        "description": "User profile and account management"
    },
    {
        "name": "Products",
        "description": "Product catalog management"
    },
    {
        "name": "Categories",
        "description": "Product category management"
    },
    {
        "name": "Cart",
        "description": "Shopping cart operations"
    },
    {
        "name": "Orders",
        "description": "Order management and processing"
    },
    {
        "name": "Payments",
        "description": "Payment processing and gateways"
    },
    {
        "name": "Shipping",
        "description": "Shipping methods and zones"
    },
    {
        "name": "Inventory",
        "description": "Inventory and warehouse management"
    },
    {
        "name": "Discounts",
        "description": "Coupons and promotional campaigns"
    },
    {
        "name": "Blog",
        "description": "Blog articles and content"
    },
    {
        "name": "Reviews",
        "description": "Product reviews and ratings"
    },
    {
        "name": "Support",
        "description": "Customer support and tickets"
    },
    {
        "name": "Notifications",
        "description": "User notifications and alerts"
    },
    {
        "name": "Ads",
        "description": "Advertisement management"
    },
    {
        "name": "Core",
        "description": "Core settings and configuration"
    }
]


# Common response schemas
class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response schema."""
    detail = serializers.CharField()
    code = serializers.CharField(required=False)
    field_errors = serializers.DictField(required=False)


class PaginatedResponseSerializer(serializers.Serializer):
    """Standard paginated response schema."""
    count = serializers.IntegerField()
    next = serializers.URLField(required=False, allow_null=True)
    previous = serializers.URLField(required=False, allow_null=True)
    results = serializers.ListField(child=serializers.DictField())


# API version info
API_VERSIONS = {
    "v1": {
        "status": "current",
        "description": "Version 1 - Initial release",
        "sunset": None
    }
}
