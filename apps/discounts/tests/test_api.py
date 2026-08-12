"""
Tests for Discounts API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.discounts.models import Discount, Coupon, Campaign
from apps.products.models import Product, Category

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
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name='Test Category',
        slug='test-category'
    )


@pytest.fixture
def product(db, category):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        category=category,
        price=100000
    )


@pytest.fixture
def discount(db):
    """Create a test discount."""
    return Discount.objects.create(
        name='Test Discount',
        discount_type='percentage',
        value=10,
        is_active=True,
        start_date='2026-08-01',
        end_date='2026-12-31'
    )


@pytest.fixture
def coupon(db, discount):
    """Create a test coupon."""
    return Coupon.objects.create(
        discount=discount,
        code='TEST10',
        usage_limit=100,
        per_user_limit=1,
        min_order_amount=100000,
        is_active=True
    )


@pytest.fixture
def campaign(db):
    """Create a test campaign."""
    return Campaign.objects.create(
        name='Test Campaign',
        slug='test-campaign',
        description='Test campaign description',
        discount_type='percentage',
        discount_value=15,
        is_active=True,
        start_date='2026-08-01',
        end_date='2026-12-31'
    )


class TestDiscountAPI:
    """Test Discount endpoints."""
    
    def test_list_discounts_admin(self, admin_client, discount):
        """Test listing discounts as admin."""
        url = reverse('api_v1:discounts_api:api-discounts-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_discount_admin(self, admin_client):
        """Test creating a discount as admin."""
        url = reverse('api_v1:discounts_api:api-discounts-create')
        data = {
            'name': 'New Discount',
            'discount_type': 'percentage',
            'value': 20,
            'is_active': True,
            'start_date': '2026-08-01',
            'end_date': '2026-12-31'
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
    
    def test_create_discount_unauthorized(self, authenticated_client):
        """Test creating a discount as non-admin."""
        url = reverse('api_v1:discounts_api:api-discounts-create')
        data = {}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCouponAPI:
    """Test Coupon endpoints."""
    
    def test_list_coupons_admin(self, admin_client, coupon):
        """Test listing coupons as admin."""
        url = reverse('api_v1:discounts_api:api-coupons-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_active_coupons(self, api_client, coupon):
        """Test listing active coupons."""
        url = reverse('api_v1:discounts_api:api-coupons-active')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_coupon_admin(self, admin_client, discount):
        """Test creating a coupon as admin."""
        url = reverse('api_v1:discounts_api:api-coupons-create')
        data = {
            'discount': discount.id,
            'code': 'NEW10',
            'usage_limit': 100,
            'per_user_limit': 1,
            'is_active': True
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == data['code']
    
    def test_validate_coupon(self, api_client, coupon):
        """Test validating a coupon."""
        url = reverse('api_v1:discounts_api:api-coupons-validate')
        data = {'code': coupon.code, 'order_amount': 100000}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['valid'] == True
    
    def test_validate_invalid_coupon(self, api_client):
        """Test validating an invalid coupon."""
        url = reverse('api_v1:discounts_api:api-coupons-validate')
        data = {'code': 'INVALID', 'order_amount': 100000}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['valid'] == False


class TestCampaignAPI:
    """Test Campaign endpoints."""
    
    def test_list_campaigns(self, api_client, campaign):
        """Test listing campaigns."""
        url = reverse('api_v1:discounts_api:api-campaigns-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_active_campaigns(self, api_client, campaign):
        """Test listing active campaigns."""
        url = reverse('api_v1:discounts_api:api-campaigns-active')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_campaign_admin(self, admin_client):
        """Test creating a campaign as admin."""
        url = reverse('api_v1:discounts_api:api-campaigns-create')
        data = {
            'name': 'New Campaign',
            'slug': 'new-campaign',
            'discount_type': 'percentage',
            'discount_value': 20,
            'is_active': True,
            'start_date': '2026-08-01',
            'end_date': '2026-12-31'
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']


class TestDiscountStatisticsAPI:
    """Test Discount statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, discount, coupon, campaign):
        """Test getting discount statistics as admin."""
        url = reverse('api_v1:discounts_api:api-discounts-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_discounts' in response.data
        assert 'total_coupons' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting discount statistics as non-admin."""
        url = reverse('api_v1:discounts_api:api-discounts-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
