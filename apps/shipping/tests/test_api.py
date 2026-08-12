"""
Tests for Shipping API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.shipping.models import ShippingZone, ShippingMethod, PickupLocation

User = get_user_model()


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Create authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create admin authenticated API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        phone_number='09123456789',
        email='test@test.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_user(
        phone_number='09123456788',
        email='admin@test.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def zone(db):
    """Create a test shipping zone."""
    return ShippingZone.objects.create(
        name='Iran',
        description='Domestic shipping zone',
        is_active=True,
        sort_order=1
    )


@pytest.fixture
def method(db, zone):
    """Create a test shipping method."""
    return ShippingMethod.objects.create(
        name='Standard Shipping',
        slug='standard-shipping',
        zone=zone,
        pricing_type='fixed',
        base_price=50000,
        estimated_delivery_min=3,
        estimated_delivery_max=7,
        is_active=True
    )


@pytest.fixture
def pickup_location(db):
    """Create a test pickup location."""
    return PickupLocation.objects.create(
        name='Main Warehouse',
        address='123 Main Street',
        city='Tehran',
        state='Tehran',
        postal_code='12345',
        country='Iran',
        phone='02112345678',
        is_active=True
    )


class TestShippingZoneAPI:
    """Test Shipping Zone endpoints."""
    
    def test_list_zones(self, api_client, zone):
        """Test listing shipping zones."""
        url = reverse('api_v1:shipping_api:api-shipping-zones-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_zone_admin(self, admin_client):
        """Test creating a shipping zone as admin."""
        url = reverse('api_v1:shipping_api:api-shipping-zones-create')
        data = {
            'name': 'Test Zone',
            'description': 'Test zone description',
            'is_active': True,
            'sort_order': 1
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
    
    def test_create_zone_unauthorized(self, authenticated_client):
        """Test creating a shipping zone as non-admin."""
        url = reverse('api_v1:shipping_api:api-shipping-zones-create')
        data = {}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestShippingMethodAPI:
    """Test Shipping Method endpoints."""
    
    def test_list_methods(self, api_client, method):
        """Test listing shipping methods."""
        url = reverse('api_v1:shipping_api:api-shipping-methods-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_available_methods(self, api_client, method):
        """Test listing available shipping methods."""
        url = reverse('api_v1:shipping_api:api-shipping-methods-available')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_method_admin(self, admin_client, zone):
        """Test creating a shipping method as admin."""
        url = reverse('api_v1:shipping_api:api-shipping-methods-create')
        data = {
            'name': 'Express Shipping',
            'slug': 'express-shipping',
            'zone': zone.id,
            'pricing_type': 'fixed',
            'base_price': 100000,
            'estimated_delivery_min': 1,
            'estimated_delivery_max': 3,
            'is_active': True
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
    
    def test_calculate_shipping_cost(self, api_client, method):
        """Test calculating shipping cost."""
        url = reverse('api_v1:shipping_api:api-shipping-methods-cost')
        data = {
            'order_total': 500000,
            'item_count': 2,
            'total_weight': 5
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


class TestPickupLocationAPI:
    """Test Pickup Location endpoints."""
    
    def test_list_pickup_locations(self, api_client, pickup_location):
        """Test listing pickup locations."""
        url = reverse('api_v1:shipping_api:api-pickup-locations-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_pickup_location_admin(self, admin_client):
        """Test creating a pickup location as admin."""
        url = reverse('api_v1:shipping_api:api-pickup-locations-create')
        data = {
            'name': 'Downtown Warehouse',
            'address': '456 Downtown Street',
            'city': 'Tehran',
            'state': 'Tehran',
            'postal_code': '67890',
            'country': 'Iran',
            'phone': '02198765432',
            'is_active': True
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']


class TestShippingStatisticsAPI:
    """Test Shipping statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, zone, method):
        """Test getting shipping statistics as admin."""
        url = reverse('api_v1:shipping_api:api-shipping-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_zones' in response.data
        assert 'total_methods' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting shipping statistics as non-admin."""
        url = reverse('api_v1:shipping_api:api-shipping-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
