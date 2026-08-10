"""
Middleware for shop-template project.
"""
import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class ThemeMiddleware(MiddlewareMixin):
    """
    Middleware to set theme-related context.
    """
    
    def process_request(self, request):
        """Process request to add theme context."""
        # Get theme configuration from database
        from apps.core.models import ThemeConfig, SiteSettings
        
        theme_config = ThemeConfig.get_active_config()
        site_settings = SiteSettings.get_instance()
        
        # Store in request for context processors
        request.theme_config = theme_config
        request.site_settings = site_settings
        
        return None


class ActivityLogMiddleware(MiddlewareMixin):
    """
    Middleware to log user activities.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Log user activities."""
        # Skip if not authenticated or not admin
        if not request.user.is_authenticated or not request.user.is_staff:
            return None
        
        # Skip for certain views
        skip_views = [
            'admin:index',
            'admin:login',
            'admin:logout',
        ]
        
        view_name = getattr(view_func, 'view_name', None) or view_func.__name__
        if view_name in skip_views:
            return None
        
        # Log the activity
        from apps.core.models import ActivityLog
        from django.utils import timezone
        
        try:
            ActivityLog.objects.create(
                user=request.user,
                action='VIEW',
                model_name=view_name,
                object_repr=str(view_kwargs),
                description=f'Viewed {view_name}',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        except Exception as e:
            logger.error(f'Error logging activity: {e}')
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to handle maintenance mode.
    """
    
    def process_request(self, request):
        """Check if site is in maintenance mode."""
        from apps.core.models import SiteSettings
        from django.urls import reverse
        
        site_settings = SiteSettings.get_instance()
        
        if site_settings and site_settings.maintenance_mode:
            # Allow admin users to access the site
            if request.user.is_authenticated and request.user.is_staff:
                return None
            
            # Redirect to maintenance page
            if request.path != reverse('maintenance'):
                return redirect('maintenance')
        
        return None


class SimpleMiddleware(MiddlewareMixin):
    """
    Simple middleware for request/response processing.
    """
    
    def process_request(self, request):
        """Process request."""
        # Add request ID for tracking
        import uuid
        request.request_id = str(uuid.uuid4())
        
        return None
    
    def process_response(self, request, response):
        """Process response."""
        # Add request ID to response headers
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        
        return response


class ReferralMiddleware(MiddlewareMixin):
    """
    Middleware to track referrals.
    """
    
    def process_request(self, request):
        """Track referral information."""
        # Get referral code from query parameters
        referral_code = request.GET.get('ref') or request.GET.get('referral')
        
        if referral_code:
            # Store in session
            request.session['referral_code'] = referral_code
            
            # Store in cookie
            response = redirect(request.path)
            response.set_cookie('referral_code', referral_code, max_age=30*24*60*60)  # 30 days
            return response
        
        return None


class CurrencyMiddleware(MiddlewareMixin):
    """
    Middleware to handle currency conversion.
    """
    
    def process_request(self, request):
        """Set default currency."""
        from apps.core.models import SiteSettings
        
        site_settings = SiteSettings.get_instance()
        
        if site_settings:
            request.currency = site_settings.currency
            request.currency_symbol = site_settings.currency_symbol
        else:
            request.currency = 'IRR'
            request.currency_symbol = 'تومان'
        
        # Allow currency override from session or cookie
        session_currency = request.session.get('currency')
        if session_currency:
            request.currency = session_currency
        
        cookie_currency = request.COOKIES.get('currency')
        if cookie_currency:
            request.currency = cookie_currency
        
        return None
