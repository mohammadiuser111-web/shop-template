"""
Custom Session Authentication
"""

from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomSessionAuthentication(SessionAuthentication):
    """
    Custom session authentication with additional validations
    """
    
    def authenticate(self, request):
        auth = super().authenticate(request)
        
        if auth is None:
            return None
        
        user, _ = auth
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationFailed('User account is disabled')
        
        return auth
