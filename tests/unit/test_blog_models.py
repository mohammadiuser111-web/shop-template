"""
Unit tests for Blog application models.
Tests BlogCategory, Tag, Article, ArticleImage models.
"""

import pytest

pytestmark = pytest.mark.django_db


class TestBlogCategory:
    """Tests for BlogCategory model"""
    
    def test_blog_category_creation(self, db):
        """Test creating a blog category"""
        from apps.blog.models import BlogCategory
        category = BlogCategory.objects.create(
            name='Technology',
            slug='technology',
            description='Technology articles',
            is_active=True,
            sort_order=0
        )
        
        assert category.name == 'Technology'
        assert category.slug == 'technology'
        assert category.description == 'Technology articles'
        assert category.is_active is True
        assert str(category) == 'Technology'
    
    def test_blog_category_str(self, db):
        """Test string representation of blog category"""
        from apps.blog.models import BlogCategory
        category = BlogCategory.objects.create(name='Programming', slug='programming')
        assert str(category) == 'Programming'
    
    def test_blog_category_name(self, db):
        """Test blog category name"""
        from apps.blog.models import BlogCategory
        category = BlogCategory.objects.create(name='Design', slug='design')
        assert category.name == 'Design'
    
    def test_blog_category_is_active(self, db):
        """Test blog category active status"""
        from apps.blog.models import BlogCategory
        active = BlogCategory.objects.create(name='Active', slug='active', is_active=True)
        inactive = BlogCategory.objects.create(name='Inactive', slug='inactive', is_active=False)
        
        assert active.is_active is True
        assert inactive.is_active is False


class TestTag:
    """Tests for Tag model"""
    
    def test_tag_creation(self, db):
        """Test creating a tag"""
        from apps.blog.models import Tag
        tag = Tag.objects.create(
            name='django',
            slug='django',
            description='Django framework',
            color='#000000'
        )
        
        assert tag.name == 'django'
        assert tag.slug == 'django'
        assert tag.description == 'Django framework'
        assert tag.color == '#000000'
        assert str(tag) == 'django'
    
    def test_tag_str(self, db):
        """Test string representation of tag"""
        from apps.blog.models import Tag
        tag = Tag.objects.create(name='python', slug='python')
        assert str(tag) == 'python'


class TestArticle:
    """Tests for Article model"""
    
    def test_article_creation(self, db):
        """Test creating an article"""
        from apps.blog.models import Article, BlogCategory
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        author = User.objects.create_user(username='author', email='author@example.com', password='pass')
        category = BlogCategory.objects.create(name='Test Category', slug='test-category')
        
        article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            author=author,
            content='Article content',
            excerpt='Article excerpt',
            status='published'
        )
        article.categories.add(category)
        
        assert article.title == 'Test Article'
        assert article.slug == 'test-article'
        assert article.author == author
        assert category in article.categories.all()
        assert article.status == 'published'
        assert str(article) == 'Test Article'
    
    def test_article_str(self, db):
        """Test string representation of article"""
        from apps.blog.models import Article
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        author = User.objects.create_user(username='author2', email='author2@example.com', password='pass')
        
        article = Article.objects.create(
            title='Another Article',
            slug='another-article',
            author=author,
            content='Content'
        )
        assert str(article) == 'Another Article'
    
    def test_article_status(self, db):
        """Test article status"""
        from apps.blog.models import Article
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        author = User.objects.create_user(username='author3', email='author3@example.com', password='pass')
        
        published = Article.objects.create(
            title='Published Article',
            slug='published-article',
            author=author,
            content='Content',
            status='published'
        )
        draft = Article.objects.create(
            title='Draft Article',
            slug='draft-article',
            author=author,
            content='Content',
            status='draft'
        )
        
        assert published.status == 'published'
        assert draft.status == 'draft'
    
    def test_article_featured_flags(self, db):
        """Test article featured flags"""
        from apps.blog.models import Article
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        author = User.objects.create_user(username='author4', email='author4@example.com', password='pass')
        
        article = Article.objects.create(
            title='Featured Article',
            slug='featured-article',
            author=author,
            content='Content',
            is_featured=True,
            is_popular=True
        )
        
        assert article.is_featured is True
        assert article.is_popular is True


class TestArticleImage:
    """Tests for ArticleImage model"""
    
    def test_article_image_creation(self, db):
        """Test creating an article image"""
        from apps.blog.models import Article, ArticleImage
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        author = User.objects.create_user(username='author5', email='author5@example.com', password='pass')
        article = Article.objects.create(
            title='Image Article',
            slug='image-article',
            author=author,
            content='Content'
        )
        
        image = ArticleImage.objects.create(
            article=article,
            image='test_image.jpg',
            alt_text='Test image',
            sort_order=0
        )
        
        assert image.article == article
        assert image.alt_text == 'Test image'
        assert image.sort_order == 0
        assert str(image) == f"{article.title} - Image 0"
    
    def test_article_image_str(self, db):
        """Test string representation of article image"""
        from apps.blog.models import Article, ArticleImage
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        author = User.objects.create_user(username='author6', email='author6@example.com', password='pass')
        article = Article.objects.create(
            title='Another Article',
            slug='another-article-2',
            author=author,
            content='Content'
        )
        
        image = ArticleImage.objects.create(
            article=article,
            image='test2.jpg',
            alt_text='Test 2',
            sort_order=1
        )
        assert str(image) == f"{article.title} - Image 1"
