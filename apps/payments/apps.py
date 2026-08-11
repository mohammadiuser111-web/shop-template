from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    verbose_name = 'پرداخت‌ها'
    
    def ready(self):
        """Override this method to register signals."""
        # Import services to make them available
        import apps.payments.services  # noqa: F401
