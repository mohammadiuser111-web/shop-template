"""
Middleware for dashboard_admin app.
Track admin activities and manage user settings.
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from .models import AdminActivity, AdminUserSettings, AdminSettings

User = get_user_model()


class AdminActivityMiddleware(MiddlewareMixin):
    """Middleware to track admin activities."""
    
    def process_request(self, request):
        """Process request and track activity."""
        # Skip if not admin
        if not request.user or not request.user.is_staff:
            return
        
        # Skip for certain paths
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/api/',
        ]
        
        path = request.path
        if any(path.startswith(p) for p in skip_paths):
            return
        
        # Track page views
        if request.method == 'GET':
            self.track_page_view(request)
    
    def process_response(self, request, response):
        """Process response."""
        return response
    
    def process_exception(self, request, exception):
        """Track exceptions."""
        if request.user and request.user.is_staff:
            AdminActivity.objects.create(
                user=request.user,
                action='error',
                model_name='Request',
                description=f'خطا در {request.path}: {str(exception)}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        return None
    
    def track_page_view(self, request):
        """Track page view."""
        path = request.path
        
        # Don't track AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return
        
        # Don't track static files
        if path.startswith('/static/') or path.startswith('/media/'):
            return
        
        AdminActivity.objects.create(
            user=request.user,
            action='read',
            model_name='Page',
            object_repr=path,
            description=f'بازدید از صفحه {path}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )


class AdminUserSettingsMiddleware(MiddlewareMixin):
    """Middleware to manage admin user settings."""
    
    def process_request(self, request):
        """Load user settings for admin users."""
        if request.user and request.user.is_authenticated and request.user.is_staff:
            # Get or create user settings
            user_settings, created = AdminUserSettings.objects.get_or_create(user=request.user)
            
            # Get global settings
            global_settings = AdminSettings.get_instance()
            
            # Attach settings to request
            request.admin_user_settings = user_settings
            request.admin_global_settings = global_settings
            
            # Set language if specified
            if user_settings.language:
                request.LANGUAGE_CODE = user_settings.language


class AdminThemeMiddleware(MiddlewareMixin):
    """Middleware to manage admin theme settings."""
    
    def process_request(self, request):
        """Apply theme settings for admin users."""
        if request.user and request.user.is_authenticated and request.user.is_staff:
            # Get user settings
            user_settings, created = AdminUserSettings.objects.get_or_create(user=request.user)
            
            # Get global settings
            global_settings = AdminSettings.get_instance()
            
            # Determine theme
            theme = user_settings.theme if user_settings.theme != 'auto' else 'light'
            
            # Set theme cookie
            if theme:
                response = self.get_response(request)
                response.set_cookie('admin_theme', theme, max_age=365*24*60*60, path='/')
                return response
        
        return self.get_response(request)


class AdminSidebarMiddleware(MiddlewareMixin):
    """Middleware to manage admin sidebar state."""
    
    def process_request(self, request):
        """Manage sidebar state for admin users."""
        if request.user and request.user.is_authenticated and request.user.is_staff:
            # Get user settings
            user_settings, created = AdminUserSettings.objects.get_or_create(user=request.user)
            
            # Check for toggle request
            if request.method == 'POST' and request.path == '/admin/toggle-sidebar/':
                user_settings.sidebar_collapsed = not user_settings.sidebar_collapsed
                user_settings.save()
            
            # Set sidebar cookie
            sidebar_state = 'collapsed' if user_settings.sidebar_collapsed else 'expanded'
            response = self.get_response(request)
            response.set_cookie('admin_sidebar', sidebar_state, max_age=365*24*60*60, path='/')
            return response
        
        return self.get_response(request)


class AdminSecurityMiddleware(MiddlewareMixin):
    """Middleware for admin security."""
    
    def process_request(self, request):
        """Check admin security."""
        if request.user and request.user.is_authenticated and request.user.is_staff:
            # Check IP restrictions
            if self.is_ip_restricted(request):
                from django.contrib.auth import logout
                logout(request)
                return None
            
            # Check time restrictions
            if self.is_time_restricted(request):
                from django.contrib.auth import logout
                logout(request)
                return None
        
        return None
    
    def is_ip_restricted(self, request):
        """Check if IP is restricted."""
        # Implement IP restriction logic
        return False
    
    def is_time_restricted(self, request):
        """Check if access is time restricted."""
        # Implement time restriction logic
        return False


# Register middlewares
__all__ = [
    'AdminActivityMiddleware',
    'AdminUserSettingsMiddleware',
    'AdminThemeMiddleware',
    'AdminSidebarMiddleware',
    'AdminSecurityMiddleware',
]
