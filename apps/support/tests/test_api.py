"""
Tests for Support API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.support.models import (
    SupportCategory, TicketPriority, TicketStatus, TicketTag, 
    Ticket, TicketMessage, FAQ, FAQCategory, CustomerSatisfaction
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
def support_category(db):
    """Create a test support category."""
    return SupportCategory.objects.create(
        name='Technical Support',
        slug='technical-support',
        description='Technical support category',
        sort_order=1
    )


@pytest.fixture
def ticket_priority(db):
    """Create a test ticket priority."""
    return TicketPriority.objects.create(
        name='High',
        color='#ef4444',
        sort_order=1
    )


@pytest.fixture
def ticket_status(db):
    """Create a test ticket status."""
    return TicketStatus.objects.create(
        name='Open',
        color='#2563eb',
        is_default=True,
        sort_order=1
    )


@pytest.fixture
def ticket_tag(db):
    """Create a test ticket tag."""
    return TicketTag.objects.create(
        name='Urgent',
        color='#ef4444'
    )


@pytest.fixture
def ticket(db, user, support_category, ticket_priority, ticket_status):
    """Create a test ticket."""
    return Ticket.objects.create(
        ticket_number='TICKET-001',
        user=user,
        category=support_category,
        priority=ticket_priority,
        status=ticket_status,
        subject='Test Ticket',
        description='Test ticket description',
        is_resolved=False
    )


@pytest.fixture
def ticket_message(db, ticket, user):
    """Create a test ticket message."""
    return TicketMessage.objects.create(
        ticket=ticket,
        user=user,
        message='Test message',
        is_internal=False
    )


@pytest.fixture
def faq_category(db):
    """Create a test FAQ category."""
    return FAQCategory.objects.create(
        name='General',
        slug='general',
        sort_order=1
    )


@pytest.fixture
def faq(db, faq_category):
    """Create a test FAQ."""
    return FAQ.objects.create(
        category=faq_category,
        question='Test Question',
        answer='Test Answer',
        sort_order=1,
        is_published=True
    )


@pytest.fixture
def satisfaction(db, ticket):
    """Create a test customer satisfaction record."""
    return CustomerSatisfaction.objects.create(
        ticket=ticket,
        rating=5,
        comment='Great service!',
        response_time=10,
        resolution_quality=5
    )


class TestSupportCategoryAPI:
    """Test Support Category endpoints."""
    
    def test_list_categories(self, api_client, support_category):
        """Test listing support categories."""
        url = reverse('api_v1:support_api:api-support-categories-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_category_admin(self, admin_client):
        """Test creating a support category as admin."""
        url = reverse('api_v1:support_api:api-support-categories-create')
        data = {
            'name': 'New Category',
            'slug': 'new-category',
            'description': 'New category description',
            'sort_order': 1
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']


class TestTicketAPI:
    """Test Ticket endpoints."""
    
    def test_list_tickets_admin(self, admin_client, ticket):
        """Test listing tickets as admin."""
        url = reverse('api_v1:support_api:api-tickets-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_tickets_user(self, authenticated_client, ticket):
        """Test listing tickets as user."""
        url = reverse('api_v1:support_api:api-tickets-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_ticket_authenticated(self, authenticated_client, support_category):
        """Test creating a ticket as authenticated user."""
        url = reverse('api_v1:support_api:api-tickets-create')
        data = {
            'category': support_category.id,
            'subject': 'Test Ticket',
            'description': 'Test ticket description',
            'priority': 'medium'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['subject'] == data['subject']
    
    def test_create_ticket_unauthenticated(self, api_client):
        """Test creating a ticket without authentication."""
        url = reverse('api_v1:support_api:api-tickets-create')
        data = {}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_retrieve_ticket(self, authenticated_client, ticket):
        """Test retrieving a ticket."""
        url = reverse('api_v1:support_api:api-tickets-retrieve', kwargs={'ticket_number': ticket.ticket_number})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['ticket_number'] == ticket.ticket_number
    
    def test_close_ticket(self, authenticated_client, ticket):
        """Test closing a ticket."""
        url = reverse('api_v1:support_api:api-tickets-close', kwargs={'ticket_number': ticket.ticket_number})
        data = {'resolution': 'Issue resolved'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_resolved'] == True


class TestTicketMessageAPI:
    """Test Ticket Message endpoints."""
    
    def test_list_messages(self, authenticated_client, ticket_message):
        """Test listing ticket messages."""
        url = reverse('api_v1:support_api:api-ticket-messages-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_message_authenticated(self, authenticated_client, ticket):
        """Test creating a ticket message as authenticated user."""
        url = reverse('api_v1:support_api:api-ticket-messages-create')
        data = {
            'ticket': ticket.id,
            'message': 'Test message',
            'is_internal': False
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == data['message']


class TestFAQAPI:
    """Test FAQ endpoints."""
    
    def test_list_faqs(self, api_client, faq):
        """Test listing FAQs."""
        url = reverse('api_v1:support_api:api-faq-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_faq_categories(self, api_client, faq_category):
        """Test listing FAQ categories."""
        url = reverse('api_v1:support_api:api-faq-categories-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_faq_admin(self, admin_client, faq_category):
        """Test creating an FAQ as admin."""
        url = reverse('api_v1:support_api:api-faq-create')
        data = {
            'category': faq_category.id,
            'question': 'New Question',
            'answer': 'New Answer',
            'sort_order': 1,
            'is_published': True
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['question'] == data['question']


class TestCustomerSatisfactionAPI:
    """Test Customer Satisfaction endpoints."""
    
    def test_create_satisfaction(self, authenticated_client, ticket):
        """Test creating a satisfaction record."""
        url = reverse('api_v1:support_api:api-customer-satisfaction-create')
        data = {
            'ticket': ticket.id,
            'rating': 5,
            'comment': 'Great service!',
            'response_time': 10,
            'resolution_quality': 5
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['rating'] == data['rating']


class TestSupportStatisticsAPI:
    """Test Support statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, ticket, faq):
        """Test getting support statistics as admin."""
        url = reverse('api_v1:support_api:api-support-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_tickets' in response.data
        assert 'total_faqs' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting support statistics as non-admin."""
        url = reverse('api_v1:support_api:api-support-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
