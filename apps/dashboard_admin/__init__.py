"""
Dashboard Admin app initialization.
"""
# Import signals to register them
from . import signals  # noqa: F401

# Default app config
default_app_config = 'apps.dashboard_admin.apps.DashboardAdminConfig'
