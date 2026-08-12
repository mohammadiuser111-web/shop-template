"""
Ads app initialization.
"""
# Default app config
from .apps import AdsConfig

__all__ = ['AdsConfig']

def get_app_config():
    """Get the app configuration."""
    return AdsConfig
