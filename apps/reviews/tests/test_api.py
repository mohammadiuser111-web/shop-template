"""
Tests for Reviews API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.reviews.models import Review, ReviewImage, ReviewComment, ReviewHelpfulness
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
def review(db, product, user):
    """Create a test review."""
    return Review.objects.create(
        product=product,
        user=user,
        rating=5,
        title='Great Product',
        comment='This is a great product!',
        status='approved',
        is_recommended=True
    )


@pytest.fixture
def review_comment(db, review, user):
    """Create a test review comment."""
    return ReviewComment.objects.create(
        review=review,
        user=user,
        content='Thanks for your review!',
        status='approved'
    )


@pytest.fixture
def helpfulness(db, review, user):
    """Create a test helpfulness vote."""
    return ReviewHelpfulness.objects.create(
        review=review,
        user=user,
        is_helpful=True
    )


class TestReviewAPI:
    """Test Review endpoints."""
    
    def test_list_reviews(self, api_client, review):
        """Test listing reviews."""
        url = reverse('api_v1:reviews_api:api-reviews-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_product_reviews(self, api_client, review, product):
        """Test listing reviews for a product."""
        url = reverse('api_v1:reviews_api:api-reviews-product', kwargs={'product_id': product.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_review_authenticated(self, authenticated_client, product):
        """Test creating a review as authenticated user."""
        url = reverse('api_v1:reviews_api:api-reviews-create')
        data = {
            'product': product.id,
            'rating': 5,
            'title': 'Great Product',
            'comment': 'This is a great product!',
            'is_recommended': True
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['rating'] == data['rating']
    
    def test_create_review_unauthenticated(self, api_client, product):
        """Test creating a review without authentication."""
        url = reverse('api_v1:reviews_api:api-reviews-create')
        data = {}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_product_rating(self, api_client, review, product):
        """Test getting product rating."""
        url = reverse('api_v1:reviews_api:api-reviews-rating', kwargs={'product_id': product.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'average_rating' in response.data
        assert 'total_reviews' in response.data
    
    def test_approve_review_admin(self, admin_client, review):
        """Test approving a review as admin."""
        review.status = 'pending'
        review.save()
        
        url = reverse('api_v1:reviews_api:api-reviews-approve', kwargs={'pk': review.id})
        response = admin_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'approved'


class TestReviewCommentAPI:
    """Test Review Comment endpoints."""
    
    def test_list_review_comments(self, api_client, review_comment):
        """Test listing review comments."""
        url = reverse('api_v1:reviews_api:api-review-comments-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_review_comment_authenticated(self, authenticated_client, review):
        """Test creating a review comment as authenticated user."""
        url = reverse('api_v1:reviews_api:api-review-comments-create')
        data = {
            'review': review.id,
            'content': 'Thanks for your review!'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == data['content']


class TestReviewHelpfulnessAPI:
    """Test Review Helpfulness endpoints."""
    
    def test_vote_helpful(self, authenticated_client, review):
        """Test voting a review as helpful."""
        url = reverse('api_v1:reviews_api:api-review-helpfulness-vote')
        data = {
            'review': review.id,
            'is_helpful': True
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_helpful'] == True
    
    def test_vote_not_helpful(self, authenticated_client, review):
        """Test voting a review as not helpful."""
        url = reverse('api_v1:reviews_api:api-review-helpfulness-vote')
        data = {
            'review': review.id,
            'is_helpful': False
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_helpful'] == False


class TestReviewStatisticsAPI:
    """Test Review statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, review, review_comment):
        """Test getting review statistics as admin."""
        url = reverse('api_v1:reviews_api:api-reviews-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_reviews' in response.data
        assert 'average_rating' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting review statistics as non-admin."""
        url = reverse('api_v1:reviews_api:api-reviews-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
