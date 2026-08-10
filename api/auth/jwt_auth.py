"""
Custom JWT Authentication
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.conf import settings


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication with additional validations
    """
    
    def authenticate(self, request):
        auth = super().authenticate(request)
        
        if auth is None:
            return None
        
        user, validated_token = auth
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationFailed('User account is disabled')
        
        # Add user to request for convenience
        request.user = user
        
        return auth
