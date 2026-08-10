"""
Template tags for theme functionality.
"""
from django import template
from django.conf import settings
import json

register = template.Library()


@register.simple_tag(takes_context=True)
def theme_vars(context):
    """
    Template tag to inject theme CSS variables.
    """
    request = context.get('request')
    theme = context.get('theme')
    
    if not theme:
        theme = {}
    
    # Get colors
    colors = theme.get('colors', settings.THEME_DEFAULT_COLORS)
    
    # Get fonts
    fonts = theme.get('fonts', settings.THEME_DEFAULT_FONTS)
    
    # Generate CSS variables
    css_vars = []
    
    # Color variables
    for key, value in colors.items():
        css_vars.append(f'--color-{key}: {value};')
    
    # Font variables
    for lang, font_info in fonts.items():
        if isinstance(font_info, dict) and 'name' in font_info:
            css_vars.append(f'--font-{lang}: "{font_info["name"]}", sans-serif;')
    
    # Additional theme variables
    if 'name' in theme:
        css_vars.append(f'--site-name: "{theme["name"]}";')
    
    # Join all variables
    css_content = '\n'.join(css_vars)
    
    return f'<style>:root {{\n{css_content}\n}}</style>'


@register.simple_tag
def theme_color(key, default='#000000'):
    """
    Get a theme color by key.
    """
    from apps.core.models import ThemeConfig
    
    theme_config = ThemeConfig.get_active_config()
    
    if theme_config:
        config = theme_config.config_json
        if 'colors' in config and key in config['colors']:
            return config['colors'][key]
    
    return default


@register.simple_tag
def theme_font(lang='persian', default='Vazir'):
    """
    Get a theme font by language.
    """
    from apps.core.models import ThemeConfig
    
    theme_config = ThemeConfig.get_active_config()
    
    if theme_config:
        config = theme_config.config_json
        if 'fonts' in config and lang in config['fonts']:
            font_info = config['fonts'][lang]
            if isinstance(font_info, dict) and 'name' in font_info:
                return font_info['name']
    
    return default


@register.simple_tag
def theme_logo():
    """
    Get the theme logo URL.
    """
    from apps.core.models import ThemeConfig, SiteSettings
    
    # First check site settings
    site_settings = SiteSettings.get_instance()
    if site_settings and site_settings.site_logo:
        return site_settings.site_logo.url
    
    # Then check theme config
    theme_config = ThemeConfig.get_active_config()
    if theme_config:
        config = theme_config.config_json
        if 'logo' in config and config['logo']:
            logo_path = config['logo']
            if logo_path.startswith('http'):
                return logo_path
            return settings.MEDIA_URL + logo_path
    
    # Return default logo
    return settings.STATIC_URL + 'icons/logo.svg'


@register.simple_tag
def theme_favicon():
    """
    Get the theme favicon URL.
    """
    from apps.core.models import SiteSettings
    
    site_settings = SiteSettings.get_instance()
    if site_settings and site_settings.site_favicon:
        return site_settings.site_favicon.url
    
    return settings.STATIC_URL + 'icons/favicon.ico'


@register.simple_tag
def theme_name():
    """
    Get the site name.
    """
    from apps.core.models import SiteSettings
    
    site_settings = SiteSettings.get_instance()
    if site_settings:
        return site_settings.site_name
    
    return 'Shop Template'


@register.simple_tag
def theme_slogan():
    """
    Get the site slogan.
    """
    from apps.core.models import SiteSettings
    
    site_settings = SiteSettings.get_instance()
    if site_settings:
        return site_settings.site_description
    
    return 'قالب حرفه‌ای فروشگاهی'


@register.filter
def format_currency(value, currency=None):
    """
    Format a number as currency.
    """
    if currency is None:
        from apps.core.models import SiteSettings
        site_settings = SiteSettings.get_instance()
        if site_settings:
            currency = site_settings.currency
        else:
            currency = 'IRR'
    
    if currency == 'IRR':
        # Iranian Rial formatting
        if value >= 1000000:
            return f'{value:,.0f} {currency}'
        return f'{value:,.0f}'
    else:
        # Other currencies
        return f'{currency} {value:,.2f}'


@register.filter
def format_price(value):
    """
    Format price with currency symbol.
    """
    from apps.core.models import SiteSettings
    
    site_settings = SiteSettings.get_instance()
    
    if site_settings:
        currency_symbol = site_settings.currency_symbol
    else:
        currency_symbol = 'تومان'
    
    if value >= 1000000:
        return f'{value:,.0f} {currency_symbol}'
    return f'{value:,.0f} {currency_symbol}'


@register.filter
def format_number(value):
    """
    Format a number with comma separators.
    """
    if value is None:
        return ''
    return f'{value:,.0f}'


@register.filter
def persian_digits(value):
    """
    Convert English digits to Persian digits.
    """
    if value is None:
        return ''
    
    digit_map = {
        '0': '۰',
        '1': '۱',
        '2': '۲',
        '3': '۳',
        '4': '۴',
        '5': '۵',
        '6': '۶',
        '7': '۷',
        '8': '۸',
        '9': '۹',
    }
    
    result = []
    for char in str(value):
        if char in digit_map:
            result.append(digit_map[char])
        else:
            result.append(char)
    
    return ''.join(result)


@register.filter
def persian_date(value):
    """
    Convert date to Persian (Jalali) date.
    """
    if value is None:
        return ''
    
    try:
        from jdatetime import datetime as jdatetime
        import jdatetime
        
        if hasattr(value, 'year'):
            # It's a datetime object
            gregorian_date = value
        else:
            # Try to parse as string
            from django.utils import timezone
            gregorian_date = timezone.datetime.strptime(str(value), '%Y-%m-%d')
        
        jalali_date = jdatetime.datetime.fromgregorian(datetime=gregorian_date)
        return jalali_date.strftime('%Y/%m/%d')
    except (ImportError, ValueError):
        return str(value)


@register.simple_tag
def ad_slot(slot_code):
    """
    Render an advertisement slot.
    """
    from apps.ads.models import AdSlot
    from django.utils import timezone
    
    try:
        slot = AdSlot.objects.get(code=slot_code, is_active=True)
        ad = slot.get_current_ad()
        
        if ad and ad.is_valid():
            # Increment impression count
            ad.increment_impressions()
            
            # Render the ad
            if ad.ad_type == 'image':
                return f'''
                <div class="ad-slot {slot.code}">
                    <a href="{ad.url}" target="{ad.target}" onclick="incrementAdClick('{ad.id}')">
                        <img src="{ad.image.url}" alt="{ad.image_alt or ad.title}" class="ad-image">
                    </a>
                </div>
                <script>
                    function incrementAdClick(adId) {{
                        fetch('/api/ads/click/' + adId + '/', {{
                            method: 'POST',
                            headers: {{
                                'X-CSRFToken': '{{ csrf_token }}',
                                'Content-Type': 'application/json'
                            }}
                        }});
                    }}
                </script>
                '''
            elif ad.ad_type == 'html':
                return f'<div class="ad-slot {slot.code}">{ad.html_content}</div>'
            elif ad.ad_type == 'script':
                return f'<div class="ad-slot {slot.code}"><script>{ad.script_content}</script></div>'
        
        return f'<div class="ad-slot {slot.code}"></div>'
    except AdSlot.DoesNotExist:
        return f'<div class="ad-slot {slot_code}"></div>'


@register.simple_tag
def render_rating(rating, max_rating=5):
    """
    Render a rating as stars.
    """
    if rating is None:
        rating = 0
    
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = max_rating - full_stars - (1 if half_star else 0)
    
    stars = []
    
    # Full stars
    for _ in range(full_stars):
        stars.append('<i class="star full"></i>')
    
    # Half star
    if half_star:
        stars.append('<i class="star half"></i>')
    
    # Empty stars
    for _ in range(empty_stars):
        stars.append('<i class="star empty"></i>')
    
    return ''.join(stars)


@register.filter
def truncate_chars(value, max_length):
    """
    Truncate a string to max_length characters.
    """
    if value is None:
        return ''
    
    value = str(value)
    if len(value) > max_length:
        return value[:max_length] + '...'
    return value


@register.filter
def truncate_words(value, max_words):
    """
    Truncate a string to max_words words.
    """
    if value is None:
        return ''
    
    words = str(value).split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return str(value)
