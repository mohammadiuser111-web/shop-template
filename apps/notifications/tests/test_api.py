"""
Tests for Notifications API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.notifications.models import (
    Notification, NotificationTemplate, EmailNotification, 
    PushNotification, SMSNotification, DeviceToken
)

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
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def notification(db, user):
    """Create a test notification."""
    return Notification.objects.create(
        user=user,
        title='Test Notification',
        message='Test notification message',
        notification_type='info',
        is_read=False,
        data={'test': 'data'}
    )


@pytest.fixture
def notification_template(db):
    """Create a test notification template."""
    return NotificationTemplate.objects.create(
        name='Test Template',
        slug='test-template',
        subject='Test Subject',
        body='Test body content',
        template_type='email',
        is_active=True
    )


@pytest.fixture
def email_notification(db, user):
    """Create a test email notification."""
    return EmailNotification.objects.create(
        user=user,
        subject='Test Email',
        message='Test email message',
        is_sent=False,
        data={'test': 'data'}
    )


@pytest.fixture
def push_notification(db, user):
    """Create a test push notification."""
    return PushNotification.objects.create(
        user=user,
        title='Test Push',
        message='Test push message',
        is_sent=False,
        data={'test': 'data'}
    )


@pytest.fixture
def sms_notification(db, user):
    """Create a test SMS notification."""
    return SMSNotification.objects.create(
        user=user,
        phone_number='09123456789',
        message='Test SMS message',
        is_sent=False
    )


@pytest.fixture
def device_token(db, user):
    """Create a test device token."""
    return DeviceToken.objects.create(
        user=user,
        token='test-device-token',
        device_type='android',
        is_active=True
    )


class TestNotificationAPI:
    """Test Notification endpoints."""
    
    def test_list_notifications(self, authenticated_client, notification):
        """Test listing notifications."""
        url = reverse('api_v1:notifications_api:api-notifications-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_unread_notifications(self, authenticated_client, notification):
        """Test listing unread notifications."""
        url = reverse('api_v1:notifications_api:api-notifications-unread')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_mark_as_read(self, authenticated_client, notification):
        """Test marking notification as read."""
        url = reverse('api_v1:notifications_api:api-notifications-mark-read', kwargs={'pk': notification.id})
        response = authenticated_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_read'] == True
    
    def test_mark_all_as_read(self, authenticated_client, notification):
        """Test marking all notifications as read."""
        url = reverse('api_v1:notifications_api:api-notifications-mark-all-read')
        response = authenticated_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_delete_notification(self, authenticated_client, notification):
        """Test deleting a notification."""
        url = reverse('api_v1:notifications_api:api-notifications-destroy', kwargs={'pk': notification.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestNotificationTemplateAPI:
    """Test Notification Template endpoints."""
    
    def test_list_templates(self, api_client, notification_template):
        """Test listing notification templates."""
        url = reverse('api_v1:notifications_api:api-notification-templates-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_template_admin(self, admin_client):
        """Test creating a notification template as admin."""
        url = reverse('api_v1:notifications_api:api-notification-templates-create')
        data = {
            'name': 'New Template',
            'slug': 'new-template',
            'subject': 'New Subject',
            'body': 'New body content',
            'template_type': 'email',
            'is_active': True
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']


class TestEmailNotificationAPI:
    """Test Email Notification endpoints."""
    
    def test_list_email_notifications_admin(self, admin_client, email_notification):
        """Test listing email notifications as admin."""
        url = reverse('api_v1:notifications_api:api-email-notifications-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_send_email_notification_admin(self, admin_client, email_notification):
        """Test sending an email notification as admin."""
        url = reverse('api_v1:notifications_api:api-email-notifications-send', kwargs={'pk': email_notification.id})
        response = admin_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_sent'] == True


class TestPushNotificationAPI:
    """Test Push Notification endpoints."""
    
    def test_list_push_notifications_admin(self, admin_client, push_notification):
        """Test listing push notifications as admin."""
        url = reverse('api_v1:notifications_api:api-push-notifications-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_send_push_notification_admin(self, admin_client, push_notification):
        """Test sending a push notification as admin."""
        url = reverse('api_v1:notifications_api:api-push-notifications-send', kwargs={'pk': push_notification.id})
        response = admin_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_sent'] == True


class TestSMSNotificationAPI:
    """Test SMS Notification endpoints."""
    
    def test_list_sms_notifications_admin(self, admin_client, sms_notification):
        """Test listing SMS notifications as admin."""
        url = reverse('api_v1:notifications_api:api-sms-notifications-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_send_sms_notification_admin(self, admin_client, sms_notification):
        """Test sending an SMS notification as admin."""
        url = reverse('api_v1:notifications_api:api-sms-notifications-send', kwargs={'pk': sms_notification.id})
        response = admin_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_sent'] == True


class TestDeviceTokenAPI:
    """Test Device Token endpoints."""
    
    def test_register_device_token(self, authenticated_client):
        """Test registering a device token."""
        url = reverse('api_v1:notifications_api:api-device-tokens-register')
        data = {
            'token': 'new-device-token',
            'device_type': 'android'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['token'] == data['token']
    
    def test_list_device_tokens(self, authenticated_client, device_token):
        """Test listing device tokens."""
        url = reverse('api_v1:notifications_api:api-device-tokens-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_remove_device_token(self, authenticated_client, device_token):
        """Test removing a device token."""
        url = reverse('api_v1:notifications_api:api-device-tokens-remove', kwargs={'token': device_token.token})
        response = authenticated_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK


class TestNotificationStatisticsAPI:
    """Test Notification statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, notification, email_notification):
        """Test getting notification statistics as admin."""
        url = reverse('api_v1:notifications_api:api-notifications-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_notifications' in response.data
        assert 'total_emails' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting notification statistics as non-admin."""
        url = reverse('api_v1:notifications_api:api-notifications-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
