"""
Custom API Exceptions
"""

from rest_framework.exceptions import APIException
from rest_framework import status


class APIValidationError(APIException):
    """
    Custom validation error exception
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error'
    
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if isinstance(detail, dict):
            self.detail = detail
        else:
            self.detail = {'error': detail, 'code': code or 'validation_error'}


class APINotFoundError(APIException):
    """
    Custom not found error exception
    """
    
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Not found'
    
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        self.detail = {
            'error': detail,
            'code': code or 'not_found'
        }


class APIPermissionError(APIException):
    """
    Custom permission error exception
    """
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied'
    
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        self.detail = {
            'error': detail,
            'code': code or 'permission_denied'
        }


class APIAuthenticationError(APIException):
    """
    Custom authentication error exception
    """
    
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed'
    
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        self.detail = {
            'error': detail,
            'code': code or 'authentication_failed'
        }


class APIRateLimitError(APIException):
    """
    Custom rate limit error exception
    """
    
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded'
    
    def __init__(self, detail=None, code=None, retry_after=None):
        if detail is None:
            detail = self.default_detail
        self.detail = {
            'error': detail,
            'code': code or 'rate_limit_exceeded'
        }
        if retry_after:
            self.detail['retry_after'] = retry_after
