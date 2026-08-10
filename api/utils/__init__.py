"""
API Utilities Package
Helper functions and utilities for the API
"""

from .validators import (
    validate_image_size,
    validate_file_size,
    validate_file_type,
    validate_phone_number,
    validate_email_domain,
)

from .helpers import (
    generate_unique_slug,
    get_client_ip,
    get_user_agent,
    format_date,
    format_datetime,
    format_currency,
    calculate_discount,
    generate_random_string,
    generate_reference_number,
)

from .exceptions import (
    APIValidationError,
    APINotFoundError,
    APIPermissionError,
    APIAuthenticationError,
    APIRateLimitError,
)

__all__ = [
    # Validators
    'validate_image_size',
    'validate_file_size',
    'validate_file_type',
    'validate_phone_number',
    'validate_email_domain',
    
    # Helpers
    'generate_unique_slug',
    'get_client_ip',
    'get_user_agent',
    'format_date',
    'format_datetime',
    'format_currency',
    'calculate_discount',
    'generate_random_string',
    'generate_reference_number',
    
    # Exceptions
    'APIValidationError',
    'APINotFoundError',
    'APIPermissionError',
    'APIAuthenticationError',
    'APIRateLimitError',
]
