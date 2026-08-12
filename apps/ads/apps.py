"""
Ads app configuration.
"""
from django.apps import AppConfig


class AdsConfig(AppConfig):
    """Configuration for ads app."""
    
    name = 'apps.ads'
    verbose_name = 'Advertisements'
    
    def ready(self):
        """Called when the app is ready."""
        # Import signals
        import apps.ads.signals
