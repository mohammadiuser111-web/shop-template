"""
Tests for Payments API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.payments.models import PaymentGateway, Transaction, Wallet

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
def gateway(db):
    """Create a test payment gateway."""
    return PaymentGateway.objects.create(
        name='Zarinpal',
        gateway_type='zarinpal',
        title='Zarinpal Gateway',
        description='Zarinpal payment gateway',
        is_active=True,
        config={'merchant_id': 'test-merchant'},
        sort_order=1
    )


@pytest.fixture
def transaction(db, user, gateway):
    """Create a test transaction."""
    return Transaction.objects.create(
        transaction_id='TXN-TEST-001',
        user=user,
        gateway=gateway,
        transaction_type='purchase',
        amount=100000,
        currency='IRR',
        status='pending',
        customer_name='Test User',
        customer_email='test@test.com'
    )


@pytest.fixture
def wallet(db, user):
    """Create a test wallet."""
    return Wallet.objects.create(
        user=user,
        balance=100000
    )


class TestPaymentGatewayAPI:
    """Test Payment Gateway endpoints."""
    
    def test_list_gateways(self, api_client, gateway):
        """Test listing payment gateways."""
        url = reverse('api_v1:payments_api:api-payment-gateways-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_active_gateways(self, api_client, gateway):
        """Test listing active payment gateways."""
        url = reverse('api_v1:payments_api:api-payment-gateways-active')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_gateway_admin(self, admin_client):
        """Test creating a payment gateway as admin."""
        url = reverse('api_v1:payments_api:api-payment-gateways-create')
        data = {
            'name': 'Test Gateway',
            'gateway_type': 'custom',
            'title': 'Test Gateway',
            'is_active': True,
            'sort_order': 1
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
    
    def test_create_gateway_unauthorized(self, authenticated_client):
        """Test creating a payment gateway as non-admin."""
        url = reverse('api_v1:payments_api:api-payment-gateways-create')
        data = {}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestTransactionAPI:
    """Test Transaction endpoints."""
    
    def test_list_transactions_admin(self, admin_client, transaction):
        """Test listing transactions as admin."""
        url = reverse('api_v1:payments_api:api-transactions-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_transactions_user(self, authenticated_client, transaction):
        """Test listing transactions as user."""
        url = reverse('api_v1:payments_api:api-transactions-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_retrieve_transaction(self, authenticated_client, transaction):
        """Test retrieving a transaction."""
        url = reverse('api_v1:payments_api:api-transactions-retrieve', kwargs={'pk': transaction.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['transaction_id'] == transaction.transaction_id
    
    def test_create_transaction(self, authenticated_client, gateway):
        """Test creating a transaction."""
        url = reverse('api_v1:payments_api:api-transactions-create')
        data = {
            'gateway': gateway.id,
            'transaction_type': 'purchase',
            'amount': 100000,
            'currency': 'IRR'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'transaction_id' in response.data


class TestWalletAPI:
    """Test Wallet endpoints."""
    
    def test_get_wallet(self, authenticated_client, wallet):
        """Test retrieving wallet."""
        url = reverse('api_v1:payments_api:api-wallet-retrieve')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['balance'] == wallet.balance
    
    def test_deposit_to_wallet(self, authenticated_client, wallet):
        """Test depositing to wallet."""
        url = reverse('api_v1:payments_api:api-wallet-deposit')
        data = {'amount': 50000, 'description': 'Test deposit'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['balance'] == wallet.balance + 50000
    
    def test_withdraw_from_wallet(self, authenticated_client, wallet):
        """Test withdrawing from wallet."""
        url = reverse('api_v1:payments_api:api-wallet-withdraw')
        data = {'amount': 50000, 'description': 'Test withdrawal'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['balance'] == wallet.balance - 50000
    
    def test_withdraw_insufficient_balance(self, authenticated_client, wallet):
        """Test withdrawing with insufficient balance."""
        url = reverse('api_v1:payments_api:api-wallet-withdraw')
        data = {'amount': 200000, 'description': 'Test withdrawal'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPaymentStatisticsAPI:
    """Test Payment statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, transaction):
        """Test getting payment statistics as admin."""
        url = reverse('api_v1:payments_api:api-payments-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_transactions' in response.data
        assert 'total_amount' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting payment statistics as non-admin."""
        url = reverse('api_v1:payments_api:api-payments-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
