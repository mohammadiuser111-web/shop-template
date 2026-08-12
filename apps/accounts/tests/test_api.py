"""
Tests for Accounts API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.accounts.models import UserAddress, UserWishlist, OTP

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
def address(db, user):
    """Create a test address."""
    return UserAddress.objects.create(
        user=user,
        first_name='Test',
        last_name='User',
        phone='09123456789',
        address_line_1='Test Address',
        address_line_2='',
        city='Test City',
        state='Test State',
        postal_code='12345',
        country='Iran',
        is_default=True
    )


@pytest.fixture
def wishlist(db, user):
    """Create a test wishlist."""
    return UserWishlist.objects.create(
        user=user,
        name='My Wishlist',
        is_default=True
    )


@pytest.fixture
def otp(db, user):
    """Create a test OTP."""
    return OTP.objects.create(
        user=user,
        code='123456',
        purpose='login',
        expires_at='2026-08-12T00:00:00Z',
        is_used=False
    )


class TestUserRegistrationAPI:
    """Test User Registration endpoints."""
    
    def test_register_user(self, api_client, db):
        """Test registering a new user."""
        url = reverse('api_v1:accounts_api:api-register-create')
        data = {
            'phone_number': '09123456780',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_register_user_validation(self, api_client, db):
        """Test user registration validation."""
        url = reverse('api_v1:accounts_api:api-register-create')
        data = {
            'phone_number': '',
            'password': '123'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'phone_number' in response.data
        assert 'password' in response.data


class TestUserLoginAPI:
    """Test User Login endpoints."""
    
    def test_login_user(self, api_client, user):
        """Test logging in a user."""
        url = reverse('api_v1:accounts_api:api-login-create')
        data = {
            'phone_number': user.phone_number,
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_credentials(self, api_client, user):
        """Test logging in with invalid credentials."""
        url = reverse('api_v1:accounts_api:api-login-create')
        data = {
            'phone_number': user.phone_number,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_validation(self, api_client):
        """Test login validation."""
        url = reverse('api_v1:accounts_api:api-login-create')
        data = {}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUserProfileAPI:
    """Test User Profile endpoints."""
    
    def test_get_profile(self, authenticated_client, user):
        """Test retrieving user profile."""
        url = reverse('api_v1:accounts_api:api-profile-retrieve')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone_number'] == user.phone_number
    
    def test_update_profile(self, authenticated_client, user):
        """Test updating user profile."""
        url = reverse('api_v1:accounts_api:api-profile-update')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == data['first_name']
    
    def test_change_password(self, authenticated_client, user):
        """Test changing password."""
        url = reverse('api_v1:accounts_api:api-profile-change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK


class TestUserAddressAPI:
    """Test User Address endpoints."""
    
    def test_list_addresses(self, authenticated_client, address):
        """Test listing user addresses."""
        url = reverse('api_v1:accounts_api:api-addresses-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_address(self, authenticated_client, user):
        """Test creating a new address."""
        url = reverse('api_v1:accounts_api:api-addresses-create')
        data = {
            'first_name': 'New',
            'last_name': 'Address',
            'phone': '09123456787',
            'address_line_1': '123 New Street',
            'city': 'New City',
            'state': 'New State',
            'postal_code': '67890',
            'country': 'Iran',
            'is_default': False
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['first_name'] == data['first_name']
    
    def test_retrieve_address(self, authenticated_client, address):
        """Test retrieving an address."""
        url = reverse('api_v1:accounts_api:api-addresses-retrieve', kwargs={'pk': address.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == address.id
    
    def test_update_address(self, authenticated_client, address):
        """Test updating an address."""
        url = reverse('api_v1:accounts_api:api-addresses-update', kwargs={'pk': address.id})
        data = {'first_name': 'Updated'}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == data['first_name']
    
    def test_delete_address(self, authenticated_client, address):
        """Test deleting an address."""
        url = reverse('api_v1:accounts_api:api-addresses-destroy', kwargs={'pk': address.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_set_default_address(self, authenticated_client, address, user):
        """Test setting default address."""
        # Create another address
        new_address = UserAddress.objects.create(
            user=user,
            first_name='New',
            last_name='Address',
            phone='09123456787',
            address_line_1='456 New Street',
            city='New City',
            state='New State',
            postal_code='67890',
            country='Iran'
        )
        
        url = reverse('api_v1:accounts_api:api-addresses-set-default', kwargs={'pk': new_address.id})
        response = authenticated_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_default'] == True


class TestUserWishlistAPI:
    """Test User Wishlist endpoints."""
    
    def test_list_wishlists(self, authenticated_client, wishlist):
        """Test listing user wishlists."""
        url = reverse('api_v1:accounts_api:api-wishlists-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_wishlist(self, authenticated_client, user):
        """Test creating a new wishlist."""
        url = reverse('api_v1:accounts_api:api-wishlists-create')
        data = {
            'name': 'New Wishlist',
            'is_default': False
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
    
    def test_retrieve_wishlist(self, authenticated_client, wishlist):
        """Test retrieving a wishlist."""
        url = reverse('api_v1:accounts_api:api-wishlists-retrieve', kwargs={'pk': wishlist.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == wishlist.id
    
    def test_update_wishlist(self, authenticated_client, wishlist):
        """Test updating a wishlist."""
        url = reverse('api_v1:accounts_api:api-wishlists-update', kwargs={'pk': wishlist.id})
        data = {'name': 'Updated Wishlist'}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == data['name']
    
    def test_delete_wishlist(self, authenticated_client, wishlist):
        """Test deleting a wishlist."""
        url = reverse('api_v1:accounts_api:api-wishlists-destroy', kwargs={'pk': wishlist.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestOTPAPI:
    """Test OTP endpoints."""
    
    def test_request_otp(self, api_client, db):
        """Test requesting OTP."""
        url = reverse('api_v1:accounts_api:api-otp-request')
        data = {
            'phone_number': '09123456780',
            'purpose': 'login'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'otp_sent' in response.data
    
    def test_verify_otp(self, api_client, otp):
        """Test verifying OTP."""
        url = reverse('api_v1:accounts_api:api-otp-verify')
        data = {
            'phone_number': otp.user.phone_number,
            'code': otp.code,
            'purpose': otp.purpose
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'verified' in response.data


class TestUserListAPI:
    """Test User list endpoint for admin."""
    
    def test_list_users_admin(self, admin_client, user):
        """Test listing users as admin."""
        url = reverse('api_v1:accounts_api:api-users-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2  # admin + user
    
    def test_list_users_unauthorized(self, authenticated_client):
        """Test listing users as non-admin."""
        url = reverse('api_v1:accounts_api:api-users-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestTokenRefreshAPI:
    """Test Token Refresh endpoint."""
    
    def test_refresh_token(self, api_client, user):
        """Test refreshing access token."""
        # First, login to get refresh token
        login_url = reverse('api_v1:accounts_api:api-login-create')
        login_data = {
            'phone_number': user.phone_number,
            'password': 'testpass123'
        }
        login_response = api_client.post(login_url, login_data, format='json')
        
        refresh_token = login_response.data['refresh']
        
        # Now refresh the token
        url = reverse('api_v1:accounts_api:api-token-refresh-create')
        data = {'refresh': refresh_token}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data


class TestUserStatisticsAPI:
    """Test User statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, user):
        """Test getting user statistics as admin."""
        url = reverse('api_v1:accounts_api:api-users-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_users' in response.data
        assert 'active_users' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting user statistics as non-admin."""
        url = reverse('api_v1:accounts_api:api-users-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
