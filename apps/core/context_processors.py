"""
Context processors for shop-template project.
"""
import json
import os
from django.conf import settings
from django.contrib.sites.models import Site


def theme_vars(request):
    """
    Context processor to inject theme variables into templates.
    """
    from apps.core.models import ThemeConfig, SiteSettings
    
    # Get theme configuration
    theme_config = ThemeConfig.get_active_config()
    
    # Get site settings
    site_settings = SiteSettings.get_instance()
    
    # Default theme configuration
    theme_data = {
        'colors': settings.THEME_DEFAULT_COLORS,
        'fonts': settings.THEME_DEFAULT_FONTS,
        'name': 'Shop Template',
        'slogan': 'قالب حرفه‌ای فروشگاهی',
        'logo': settings.STATIC_URL + 'icons/logo.svg',
        'favicon': settings.STATIC_URL + 'icons/favicon.ico',
    }
    
    # Override with database configuration if available
    if theme_config:
        config = theme_config.config_json
        theme_data.update({
            'colors': config.get('colors', theme_data['colors']),
            'fonts': config.get('fonts', theme_data['fonts']),
            'name': config.get('name', theme_data['name']),
            'slogan': config.get('slogan', theme_data['slogan']),
        })
        
        # Handle logo path
        logo_path = config.get('logo', '')
        if logo_path:
            if logo_path.startswith('http'):
                theme_data['logo'] = logo_path
            else:
                theme_data['logo'] = settings.MEDIA_URL + logo_path
    
    # Override with site settings if available
    if site_settings:
        if site_settings.site_logo:
            theme_data['logo'] = site_settings.site_logo.url
        if site_settings.site_favicon:
            theme_data['favicon'] = site_settings.site_favicon.url
        theme_data['name'] = site_settings.site_name or theme_data['name']
        theme_data['slogan'] = site_settings.site_description or theme_data['slogan']
    
    # Generate CSS variables
    css_variables = ''
    if 'colors' in theme_data and isinstance(theme_data['colors'], dict):
        for key, value in theme_data['colors'].items():
            css_variables += f'--color-{key}: {value};\n'
    
    if 'fonts' in theme_data and isinstance(theme_data['fonts'], dict):
        for lang, font in theme_data['fonts'].items():
            if 'name' in font:
                css_variables += f'--font-{lang}: "{font["name"]}", sans-serif;\n'
    
    # Get current site
    current_site = Site.objects.get_current() if hasattr(Site, 'objects') else None
    
    return {
        'theme': theme_data,
        'theme_css_variables': css_variables,
        'site_settings': site_settings,
        'current_site': current_site,
    }


def site_settings(request):
    """
    Context processor to inject site settings into templates.
    """
    from apps.core.models import SiteSettings
    
    site_settings = SiteSettings.get_instance()
    
    return {
        'site_settings': site_settings,
    }


def notifications(request):
    """
    Context processor to inject user notifications into templates.
    """
    if not request.user.is_authenticated:
        return {'user_notifications': []}
    
    from apps.notifications.models import Notification
    
    notifications = Notification.objects.filter(
        user=request.user,
        is_archived=False
    ).order_by('-priority', '-created_at')[:10]
    
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False,
        is_archived=False
    ).count()
    
    return {
        'user_notifications': notifications,
        'unread_notifications_count': unread_count,
    }


def cart(request):
    """
    Context processor to inject cart information into templates.
    """
    from apps.cart.models import Cart
    
    cart = None
    if request.user.is_authenticated:
        # Try to get user cart
        cart = Cart.objects.filter(user=request.user, cart_type='user').first()
        if not cart:
            # Create a new cart if doesn't exist
            cart = Cart.objects.create(user=request.user, cart_type='user')
    else:
        # Try to get session cart
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key, cart_type='session').first()
            if not cart:
                cart = Cart.objects.create(session_key=session_key, cart_type='session')
    
    return {
        'cart': cart,
        'cart_item_count': cart.get_item_count() if cart else 0,
    }


def wishlist(request):
    """
    Context processor to inject wishlist information into templates.
    """
    if not request.user.is_authenticated:
        return {'wishlist_item_count': 0}
    
    wishlist_count = request.user.wishlist_items.count()
    
    return {
        'wishlist_item_count': wishlist_count,
    }


def currency(request):
    """
    Context processor to inject currency information into templates.
    """
    from apps.core.models import SiteSettings
    
    site_settings = SiteSettings.get_instance()
    
    currency = site_settings.currency if site_settings else 'IRR'
    currency_symbol = site_settings.currency_symbol if site_settings else 'تومان'
    
    return {
        'currency': currency,
        'currency_symbol': currency_symbol,
    }


def user_permissions(request):
    """
    Context processor to inject user permissions into templates.
    """
    if not request.user.is_authenticated:
        return {'user_permissions': []}
    
    permissions = []
    if request.user.is_superuser:
        permissions.append('superuser')
    
    if request.user.is_staff:
        permissions.append('staff')
    
    # Add custom permissions
    for perm in request.user.user_permissions.all():
        permissions.append(perm.codename)
    
    # Add group permissions
    for group in request.user.groups.all():
        for perm in group.permissions.all():
            if perm.codename not in permissions:
                permissions.append(perm.codename)
    
    return {
        'user_permissions': permissions,
    }
