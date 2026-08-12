"""
Tests for Core API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.core.models import SiteSettings, ThemeConfig


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def site_settings(db):
    """Create site settings for testing."""
    return SiteSettings.objects.create(
        site_name="Test Shop",
        site_description="Test shop description",
        site_logo="/static/logo.png",
        contact_email="test@test.com",
        contact_phone="1234567890"
    )


@pytest.fixture
def theme_config(db):
    """Create theme config for testing."""
    return ThemeConfig.objects.create(
        name="Default Theme",
        primary_color="#2563eb",
        secondary_color="#7c3aed",
        font_family="Inter"
    )


class TestSiteSettingsAPI:
    """Test SiteSettings API endpoints."""
    
    def test_get_site_settings(self, api_client, site_settings):
        """Test retrieving site settings."""
        url = reverse('api_v1:core_api:api-settings-retrieve')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'site_name' in response.data
        assert response.data['site_name'] == site_settings.site_name
    
    def test_get_site_settings_not_found(self, api_client):
        """Test retrieving site settings when none exist."""
        url = reverse('api_v1:core_api:api-settings-retrieve')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestThemeConfigAPI:
    """Test ThemeConfig API endpoints."""
    
    def test_get_theme_config(self, api_client, theme_config):
        """Test retrieving theme configuration."""
        url = reverse('api_v1:core_api:api-theme-retrieve')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'primary_color' in response.data
        assert response.data['primary_color'] == theme_config.primary_color
    
    def test_get_theme_config_not_found(self, api_client):
        """Test retrieving theme config when none exist."""
        url = reverse('api_v1:core_api:api-theme-retrieve')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestHealthCheckAPI:
    """Test health check endpoint."""
    
    def test_health_check(self, api_client):
        """Test health check endpoint."""
        url = reverse('api_v1:core_api:api-health-check')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'


class TestContactAPI:
    """Test contact form API."""
    
    def test_contact_form_submission(self, api_client):
        """Test submitting contact form."""
        url = reverse('api_v1:core_api:api-contact-create')
        data = {
            'name': 'Test User',
            'email': 'test@test.com',
            'subject': 'Test Subject',
            'message': 'Test message content'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'name' in response.data
        assert response.data['name'] == data['name']
    
    def test_contact_form_validation(self, api_client):
        """Test contact form validation."""
        url = reverse('api_v1:core_api:api-contact-create')
        data = {
            'name': '',
            'email': 'invalid-email'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
        assert 'email' in response.data
