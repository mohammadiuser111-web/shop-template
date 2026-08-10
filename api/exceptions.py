"""
API Exception Handlers
Custom exception handling for the API
"""

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import (
    APIException, 
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAuthenticated,
    Throttled,
    ValidationError
)
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for API exceptions
    """
    
    # Call REST framework's default exception handler first
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        # Customize the error response
        error_data = {
            'status': 'error',
            'code': get_error_code(exc),
            'message': get_error_message(exc),
            'details': get_error_details(exc, response)
        }
        
        # Log the exception
        logger.error(
            f"API Error: {error_data['code']} - {error_data['message']}",
            exc_info=True
        )
        
        response.data = error_data
        response.status_code = get_status_code(exc, response)
        
        return response
    
    # Handle other exceptions
    error_data = {
        'status': 'error',
        'code': 'server_error',
        'message': str(exc),
        'details': {}
    }
    
    logger.error(
        f"API Error: {error_data['code']} - {error_data['message']}",
        exc_info=True
    )
    
    return Response(
        error_data,
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def get_error_code(exc):
    """
    Get error code from exception
    """
    
    if isinstance(exc, ValidationError):
        return 'validation_error'
    elif isinstance(exc, AuthenticationFailed):
        return 'authentication_failed'
    elif isinstance(exc, PermissionDenied):
        return 'permission_denied'
    elif isinstance(exc, NotFound):
        return 'not_found'
    elif isinstance(exc, MethodNotAllowed):
        return 'method_not_allowed'
    elif isinstance(exc, NotAuthenticated):
        return 'not_authenticated'
    elif isinstance(exc, Throttled):
        return 'rate_limit_exceeded'
    elif isinstance(exc, APIException):
        return getattr(exc, 'default_code', 'api_error')
    else:
        return 'server_error'


def get_error_message(exc):
    """
    Get error message from exception
    """
    
    if isinstance(exc, ValidationError):
        return 'Validation error'
    elif isinstance(exc, AuthenticationFailed):
        return 'Authentication failed'
    elif isinstance(exc, PermissionDenied):
        return 'Permission denied'
    elif isinstance(exc, NotFound):
        return 'Resource not found'
    elif isinstance(exc, MethodNotAllowed):
        return 'Method not allowed'
    elif isinstance(exc, NotAuthenticated):
        return 'Authentication required'
    elif isinstance(exc, Throttled):
        return 'Rate limit exceeded'
    elif isinstance(exc, APIException):
        return exc.detail if isinstance(exc.detail, str) else 'API error'
    else:
        return 'Internal server error'


def get_error_details(exc, response):
    """
    Get error details from exception and response
    """
    
    if isinstance(exc, ValidationError):
        # Format validation errors
        details = {}
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            for field, errors in exc.detail.items():
                if isinstance(errors, list):
                    details[field] = errors
                else:
                    details[field] = [str(errors)]
        return details
    elif isinstance(exc, Throttled):
        return {
            'retry_after': exc.wait()
        }
    elif isinstance(exc, APIException):
        if isinstance(exc.detail, dict):
            return exc.detail
        return {'message': str(exc.detail)}
    else:
        return {}


def get_status_code(exc, response):
    """
    Get HTTP status code from exception
    """
    
    if isinstance(exc, ValidationError):
        return status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, AuthenticationFailed):
        return status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, PermissionDenied):
        return status.HTTP_403_FORBIDDEN
    elif isinstance(exc, NotFound):
        return status.HTTP_404_NOT_FOUND
    elif isinstance(exc, MethodNotAllowed):
        return status.HTTP_405_METHOD_NOT_ALLOWED
    elif isinstance(exc, NotAuthenticated):
        return status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, Throttled):
        return status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exc, APIException):
        return getattr(exc, 'status_code', status.HTTP_400_BAD_REQUEST)
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
