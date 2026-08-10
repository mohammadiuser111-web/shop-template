"""
Helper Functions
"""

import random
import string
import re
from datetime import datetime, date
from django.utils.text import slugify
from django.db.models import Q
from django.conf import settings


def generate_unique_slug(model, field_name, value, max_length=200):
    """
    Generate a unique slug for a model field
    """
    slug = slugify(value)[:max_length]
    original_slug = slug
    counter = 1
    
    while model.objects.filter(**{field_name: slug}).exists():
        slug = f"{original_slug}-{counter}"
        counter += 1
        if len(slug) > max_length:
            slug = slug[:max_length]
    
    return slug


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Get user agent from request
    """
    return request.META.get('HTTP_USER_AGENT', '')


def format_date(date_obj, format_str='%Y-%m-%d'):
    """
    Format date object to string
    """
    if date_obj is None:
        return ''
    return date_obj.strftime(format_str)


def format_datetime(datetime_obj, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Format datetime object to string
    """
    if datetime_obj is None:
        return ''
    return datetime_obj.strftime(format_str)


def format_currency(amount, currency_symbol='$', decimal_places=2):
    """
    Format amount as currency
    """
    if amount is None:
        amount = 0
    return f"{currency_symbol}{float(amount):.{decimal_places}f}"


def calculate_discount(price, discount_type, discount_value):
    """
    Calculate discounted price
    """
    if discount_type == 'percentage':
        return price * (1 - discount_value / 100)
    elif discount_type == 'fixed_amount':
        return price - discount_value
    elif discount_type == 'fixed_price':
        return discount_value
    return price


def generate_random_string(length=10, chars=None):
    """
    Generate random string
    """
    if chars is None:
        chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_reference_number(prefix='REF', length=8):
    """
    Generate reference number
    """
    random_part = generate_random_string(length)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{prefix}-{timestamp}-{random_part}"


def get_model_field(model, field_name, default=None):
    """
    Get field value from model
    """
    try:
        return getattr(model, field_name, default)
    except Exception:
        return default


def get_related_model(model, related_name, default=None):
    """
    Get related model instance
    """
    try:
        return getattr(model, related_name, default)
    except Exception:
        return default


def clean_html(html):
    """
    Clean HTML content
    """
    if not html:
        return ''
    
    # Remove script tags
    html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove style tags
    html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove other potentially dangerous tags
    html = re.sub(r'<(iframe|frame|object|embed|applet|form).*?>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    return html
