"""
Tests for Orders API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.products.models import Product, Category
from apps.accounts.models import UserAddress

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
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_user(
        phone_number='09123456788',
        email='admin@test.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name='Test Category',
        slug='test-category',
        description='Test category description'
    )


@pytest.fixture
def product(db, category):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        category=category,
        price=100000,
        description='Test product description',
        is_active=True
    )


@pytest.fixture
def address(db, user):
    """Create a test address."""
    return UserAddress.objects.create(
        user=user,
        first_name='Test',
        last_name='User',
        phone='09123456789',
        address_line_1='Test Address',
        city='Test City',
        state='Test State',
        postal_code='12345',
        country='Iran',
        is_default=True
    )


@pytest.fixture
def order(db, user, product, address):
    """Create a test order."""
    order = Order.objects.create(
        user=user,
        order_number='TEST-001',
        status='pending',
        shipping_address=address,
        billing_address=address,
        subtotal=100000,
        total_amount=100000,
        currency='IRR'
    )
    
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=100000
    )
    
    return order


class TestOrderListAPI:
    """Test Order list endpoint."""
    
    def test_list_orders_admin(self, admin_client, order):
        """Test listing orders as admin."""
        url = reverse('api_v1:orders_api:api-orders-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_orders_user(self, authenticated_client, order):
        """Test listing orders as regular user."""
        url = reverse('api_v1:orders_api:api-orders-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_orders_unauthenticated(self, api_client):
        """Test listing orders without authentication."""
        url = reverse('api_v1:orders_api:api-orders-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOrderRetrieveAPI:
    """Test Order retrieve endpoint."""
    
    def test_retrieve_order(self, authenticated_client, order):
        """Test retrieving an order."""
        url = reverse('api_v1:orders_api:api-orders-retrieve', kwargs={'order_number': order.order_number})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['order_number'] == order.order_number
    
    def test_retrieve_nonexistent_order(self, authenticated_client):
        """Test retrieving a non-existent order."""
        url = reverse('api_v1:orders_api:api-orders-retrieve', kwargs={'order_number': 'NONEXISTENT'})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestOrderCreateAPI:
    """Test Order create endpoint."""
    
    def test_create_order(self, authenticated_client, product, address, user):
        """Test creating an order."""
        url = reverse('api_v1:orders_api:api-orders-create')
        data = {
            'shipping_address_id': address.id,
            'billing_address_id': address.id,
            'payment_method': 'cash_on_delivery',
            'shipping_method': 'standard',
            'notes': 'Test order'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'order_number' in response.data
    
    def test_create_order_unauthenticated(self, api_client):
        """Test creating an order without authentication."""
        url = reverse('api_v1:orders_api:api-orders-create')
        data = {}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOrderCancelAPI:
    """Test Order cancel endpoint."""
    
    def test_cancel_order(self, authenticated_client, order):
        """Test cancelling an order."""
        url = reverse('api_v1:orders_api:api-orders-cancel', kwargs={'order_number': order.order_number})
        data = {'reason': 'Changed mind'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'
    
    def test_cancel_order_invalid_status(self, authenticated_client, order):
        """Test cancelling an order with invalid status."""
        order.status = 'delivered'
        order.save()
        
        url = reverse('api_v1:orders_api:api-orders-cancel', kwargs={'order_number': order.order_number})
        data = {'reason': 'Test'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestOrderStatisticsAPI:
    """Test Order statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, order):
        """Test getting order statistics as admin."""
        url = reverse('api_v1:orders_api:api-orders-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'today' in response.data
        assert 'this_week' in response.data
        assert 'this_month' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting order statistics as non-admin."""
        url = reverse('api_v1:orders_api:api-orders-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
