# ============================================
# Pytest Fixtures for Shop Template
# ============================================

"""
Pytest fixtures for Django testing.
"""

import pytest
import os
import sys

# Add project directory to path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

# Set Django settings before any imports
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Pytest Django Configuration
pytest_plugins = ['pytest_django']


# ============================================
# Factory Fixtures
# ============================================

@pytest.fixture
def user_factory():
    """Factory for creating User instances"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    def _create_user(**kwargs):
        defaults = {
            'phone_number': '+1234567890',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _create_user


@pytest.fixture
def staff_user_factory(user_factory):
    """Factory for creating Staff User instances"""
    def _create_staff_user(**kwargs):
        defaults = {'is_staff': True}
        defaults.update(kwargs)
        return user_factory(**defaults)
    return _create_staff_user


@pytest.fixture
def admin_user_factory(user_factory):
    """Factory for creating Admin User instances"""
    def _create_admin_user(**kwargs):
        defaults = {'is_staff': True, 'is_superuser': True}
        defaults.update(kwargs)
        return user_factory(**defaults)
    return _create_admin_user
