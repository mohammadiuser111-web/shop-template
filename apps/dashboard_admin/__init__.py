# ============================================
# Dashboard Admin App Configuration
# ============================================

"""
Dashboard Admin application for Shop Template.
Provides custom admin panel and dashboard functionality.
"""

# Import signals only after Django is fully loaded
import django
from django.apps import apps

# Check if Django is ready before importing signals
if apps.ready:
    from . import signals  # noqa: F401
else:
    # Use AppConfig to defer signal registration
    default_app_config = 'apps.dashboard_admin.apps.DashboardAdminConfig'
