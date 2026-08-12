"""
Tests for Blog API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.blog.models import BlogCategory, Tag, Article, Comment

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
    """Create a test blog category."""
    return BlogCategory.objects.create(
        name='Test Category',
        slug='test-category',
        description='Test category description'
    )


@pytest.fixture
def tag(db):
    """Create a test tag."""
    return Tag.objects.create(
        name='Test Tag',
        slug='test-tag'
    )


@pytest.fixture
def article(db, category, user):
    """Create a test article."""
    return Article.objects.create(
        title='Test Article',
        slug='test-article',
        category=category,
        author=user,
        content='Test article content',
        excerpt='Test article excerpt',
        status='published',
        is_featured=True
    )


@pytest.fixture
def comment(db, article, user):
    """Create a test comment."""
    return Comment.objects.create(
        article=article,
        user=user,
        content='Test comment content',
        status='approved'
    )


class TestBlogCategoryAPI:
    """Test Blog Category endpoints."""
    
    def test_list_categories(self, api_client, category):
        """Test listing blog categories."""
        url = reverse('api_v1:blog_api:api-blog-categories-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_category_admin(self, admin_client):
        """Test creating a blog category as admin."""
        url = reverse('api_v1:blog_api:api-blog-categories-create')
        data = {
            'name': 'New Category',
            'slug': 'new-category',
            'description': 'New category description'
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']


class TestTagAPI:
    """Test Tag endpoints."""
    
    def test_list_tags(self, api_client, tag):
        """Test listing tags."""
        url = reverse('api_v1:blog_api:api-tags-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_tag_admin(self, admin_client):
        """Test creating a tag as admin."""
        url = reverse('api_v1:blog_api:api-tags-create')
        data = {'name': 'New Tag', 'slug': 'new-tag'}
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']


class TestArticleAPI:
    """Test Article endpoints."""
    
    def test_list_articles(self, api_client, article):
        """Test listing articles."""
        url = reverse('api_v1:blog_api:api-articles-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_published_articles(self, api_client, article):
        """Test listing published articles."""
        url = reverse('api_v1:blog_api:api-articles-published')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_featured_articles(self, api_client, article):
        """Test listing featured articles."""
        url = reverse('api_v1:blog_api:api-articles-featured')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_retrieve_article(self, api_client, article):
        """Test retrieving an article."""
        url = reverse('api_v1:blog_api:api-articles-retrieve', kwargs={'slug': article.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == article.title
    
    def test_create_article_admin(self, admin_client, category):
        """Test creating an article as admin."""
        url = reverse('api_v1:blog_api:api-articles-create')
        data = {
            'title': 'New Article',
            'slug': 'new-article',
            'category': category.id,
            'content': 'New article content',
            'excerpt': 'New article excerpt',
            'status': 'published',
            'is_featured': True
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == data['title']
    
    def test_create_article_unauthorized(self, authenticated_client):
        """Test creating an article as non-admin."""
        url = reverse('api_v1:blog_api:api-articles-create')
        data = {}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_search_articles(self, api_client, article):
        """Test searching articles."""
        url = reverse('api_v1:blog_api:api-articles-search')
        data = {'query': 'Test'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


class TestCommentAPI:
    """Test Comment endpoints."""
    
    def test_list_comments(self, api_client, comment):
        """Test listing comments."""
        url = reverse('api_v1:blog_api:api-comments-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_comment_authenticated(self, authenticated_client, article):
        """Test creating a comment as authenticated user."""
        url = reverse('api_v1:blog_api:api-comments-create')
        data = {
            'article': article.id,
            'content': 'New comment content'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == data['content']
    
    def test_create_comment_unauthenticated(self, api_client, article):
        """Test creating a comment without authentication."""
        url = reverse('api_v1:blog_api:api-comments-create')
        data = {}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_approve_comment_admin(self, admin_client, comment):
        """Test approving a comment as admin."""
        comment.status = 'pending'
        comment.save()
        
        url = reverse('api_v1:blog_api:api-comments-approve', kwargs={'pk': comment.id})
        response = admin_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'approved'


class TestBlogStatisticsAPI:
    """Test Blog statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, category, article, comment):
        """Test getting blog statistics as admin."""
        url = reverse('api_v1:blog_api:api-blog-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_articles' in response.data
        assert 'total_categories' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting blog statistics as non-admin."""
        url = reverse('api_v1:blog_api:api-blog-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
