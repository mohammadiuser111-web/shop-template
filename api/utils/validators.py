"""
Custom Validators
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
import os
from PIL import Image


def validate_image_size(value, max_width=None, max_height=None, max_size_mb=5):
    """
    Validate image dimensions and file size
    """
    if not value:
        return
    
    try:
        img = Image.open(value)
        width, height = img.size
        
        if max_width and width > max_width:
            raise ValidationError(
                _('Image width must be less than %(max_width)spx. Current: %(width)spx') % {
                    'max_width': max_width,
                    'width': width
                }
            )
        
        if max_height and height > max_height:
            raise ValidationError(
                _('Image height must be less than %(max_height)spx. Current: %(height)spx') % {
                    'max_height': max_height,
                    'height': height
                }
            )
        
        # Check file size
        file_size = len(value.read())
        value.seek(0)  # Reset file pointer
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            raise ValidationError(
                _('Image size must be less than %(max_size)smb. Current: %(size).2fmb') % {
                    'max_size': max_size_mb,
                    'size': file_size / (1024 * 1024)
                }
            )
    
    except Exception as e:
        raise ValidationError(_('Invalid image file: %(error)s') % {'error': str(e)})


def validate_file_size(value, max_size_mb=10):
    """
    Validate file size
    """
    if not value:
        return
    
    try:
        file_size = len(value.read())
        value.seek(0)  # Reset file pointer
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            raise ValidationError(
                _('File size must be less than %(max_size)smb. Current: %(size).2fmb') % {
                    'max_size': max_size_mb,
                    'size': file_size / (1024 * 1024)
                }
            )
    except Exception as e:
        raise ValidationError(_('Invalid file: %(error)s') % {'error': str(e)})


def validate_file_type(value, allowed_types=None):
    """
    Validate file type by extension
    """
    if not value:
        return
    
    if allowed_types is None:
        allowed_types = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx']
    
    try:
        ext = os.path.splitext(value.name)[1][1:].lower()
        
        if ext not in allowed_types:
            raise ValidationError(
                _('File type not allowed. Allowed types: %(types)s') % {
                    'types': ', '.join(allowed_types)
                }
            )
    except Exception as e:
        raise ValidationError(_('Invalid file type: %(error)s') % {'error': str(e)})


def validate_phone_number(value):
    """
    Validate phone number format
    """
    if not value:
        return
    
    # Basic phone number validation
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    
    if not phone_regex.match(value):
        raise ValidationError(
            _('Enter a valid phone number. Example: +1234567890')
        )


def validate_email_domain(value, allowed_domains=None):
    """
    Validate email domain
    """
    if not value:
        return
    
    if allowed_domains is None:
        return  # No restrictions
    
    try:
        domain = value.split('@')[1].lower()
        
        if domain not in allowed_domains:
            raise ValidationError(
                _('Email domain not allowed. Allowed domains: %(domains)s') % {
                    'domains': ', '.join(allowed_domains)
                }
            )
    except IndexError:
        raise ValidationError(_('Invalid email format'))
