from django.apps import AppConfig


class DashboardAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard_admin'
    verbose_name = 'پنل مدیریت'
    
    def ready(self):
        """Override this method to register signals."""
        # Import and register signals
        import apps.dashboard_admin.signals  # noqa: F401
