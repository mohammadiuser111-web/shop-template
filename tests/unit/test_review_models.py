"""
Unit tests for Review application models.
Tests Review, ReviewImage, ReviewVideo, ReviewComment, ReviewHelpfulness models.
"""

import pytest

pytestmark = pytest.mark.django_db


class TestReview:
    """Tests for Review model"""
    
    def test_review_creation(self, db):
        """Test creating a review"""
        from apps.reviews.models import Review
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD001',
            name='Review Product',
            slug='review-product',
            regular_price=50.00
        )
        
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            title='Great Product',
            content='This is a great product',
            is_approved=True
        )
        
        assert review.product == product
        assert review.author_name == 'Test User'
        assert review.rating == 5
        assert review.title == 'Great Product'
        assert review.content == 'This is a great product'
        assert review.is_approved is True
        assert str(review) == '5 star review for Review Product'
    
    def test_review_str(self, db):
        """Test string representation of review"""
        from apps.reviews.models import Review
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD002',
            name='Str Product',
            slug='str-product',
            regular_price=50.00
        )
        
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=4,
            content='Good product'
        )
        assert str(review) == '4 star review for Str Product'
    
    def test_review_rating(self, db):
        """Test review rating"""
        from apps.reviews.models import Review
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD003',
            name='Rating Product',
            slug='rating-product',
            regular_price=50.00
        )
        
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=3,
            content='Average product'
        )
        assert review.rating == 3
    
    def test_review_approval_status(self, db):
        """Test review approval status"""
        from apps.reviews.models import Review
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD004',
            name='Approval Product',
            slug='approval-product',
            regular_price=50.00
        )
        
        approved = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            content='Great',
            is_approved=True
        )
        pending = Review.objects.create(
            product=product,
            author_name='Test User 2',
            author_email='test2@example.com',
            rating=4,
            content='Good',
            is_approved=False
        )
        
        assert approved.is_approved is True
        assert pending.is_approved is False
    
    def test_review_verified_purchase(self, db):
        """Test review verified purchase status"""
        from apps.reviews.models import Review
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD005',
            name='Verified Product',
            slug='verified-product',
            regular_price=50.00
        )
        
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            content='Great',
            is_verified_purchase=True
        )
        assert review.is_verified_purchase is True
    
    def test_review_helpfulness(self, db):
        """Test review helpfulness counts"""
        from apps.reviews.models import Review
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD006',
            name='Helpful Product',
            slug='helpful-product',
            regular_price=50.00
        )
        
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            content='Great',
            helpful_count=10,
            not_helpful_count=2
        )
        
        assert review.helpful_count == 10
        assert review.not_helpful_count == 2
    
    def test_review_created_at(self, db):
        """Test review created_at timestamp"""
        from apps.reviews.models import Review
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD007',
            name='Time Product',
            slug='time-product',
            regular_price=50.00
        )
        
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            content='Great'
        )
        assert review.created_at is not None
    
    def test_review_updated_at(self, db):
        """Test review updated_at timestamp"""
        from apps.reviews.models import Review
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD008',
            name='Updated Product',
            slug='updated-product',
            regular_price=50.00
        )
        
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            content='Great'
        )
        assert review.updated_at is not None


class TestReviewImage:
    """Tests for ReviewImage model"""
    
    def test_review_image_creation(self, db):
        """Test creating a review image"""
        from apps.reviews.models import ReviewImage
        image = ReviewImage.objects.create(
            image='test_image.jpg',
            caption='Test image'
        )
        
        assert image.caption == 'Test image'
        assert str(image) == f"Image {image.id}"
    
    def test_review_image_str(self, db):
        """Test string representation of review image"""
        from apps.reviews.models import ReviewImage
        image = ReviewImage.objects.create(image='test2.jpg')
        assert str(image) == f"Image {image.id}"
    
    def test_review_image_caption(self, db):
        """Test review image caption"""
        from apps.reviews.models import ReviewImage
        image = ReviewImage.objects.create(
            image='caption_test.jpg',
            caption='This is a caption'
        )
        assert image.caption == 'This is a caption'


class TestReviewVideo:
    """Tests for ReviewVideo model"""
    
    def test_review_video_creation(self, db):
        """Test creating a review video"""
        from apps.reviews.models import ReviewVideo
        video = ReviewVideo.objects.create(
            video='videos/test.mp4',
            caption='Test video'
        )
        
        assert video.video == 'videos/test.mp4'
        assert video.caption == 'Test video'
        assert str(video) == f"Video {video.id}"
    
    def test_review_video_str(self, db):
        """Test string representation of review video"""
        from apps.reviews.models import ReviewVideo
        video = ReviewVideo.objects.create(video='videos/test2.mp4')
        assert str(video) == f"Video {video.id}"


class TestReviewComment:
    """Tests for ReviewComment model"""
    
    def test_review_comment_creation(self, db):
        """Test creating a review comment"""
        from apps.reviews.models import Review, ReviewComment
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD009',
            name='Comment Product',
            slug='comment-product',
            regular_price=50.00
        )
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            content='Great product'
        )
        
        comment = ReviewComment.objects.create(
            review=review,
            content='I agree with this review'
        )
        
        assert comment.review == review
        assert comment.content == 'I agree with this review'
        assert str(comment) == f"Comment on review {review.id}"
    
    def test_review_comment_str(self, db):
        """Test string representation of review comment"""
        from apps.reviews.models import Review, ReviewComment
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD010',
            name='Comment Str Product',
            slug='comment-str-product',
            regular_price=50.00
        )
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            content='Great product'
        )
        
        comment = ReviewComment.objects.create(
            review=review,
            content='Good review'
        )
        assert str(comment) == f"Comment on review {review.id}"


class TestReviewHelpfulness:
    """Tests for ReviewHelpfulness model"""
    
    def test_review_helpfulness_creation(self, db):
        """Test creating a review helpfulness"""
        from apps.reviews.models import Review, ReviewHelpfulness
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD011',
            name='Helpfulness Product',
            slug='helpfulness-product',
            regular_price=50.00
        )
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            content='Great product'
        )
        
        helpfulness = ReviewHelpfulness.objects.create(
            review=review,
            is_helpful=True
        )
        
        assert helpfulness.review == review
        assert helpfulness.is_helpful is True
        assert str(helpfulness) == f"True - {review}"
    
    def test_review_helpfulness_str(self, db):
        """Test string representation of review helpfulness"""
        from apps.reviews.models import Review, ReviewHelpfulness
        from apps.products.models import Product
        
        product = Product.objects.create(
            sku='PROD012',
            name='Helpfulness Str Product',
            slug='helpfulness-str-product',
            regular_price=50.00
        )
        review = Review.objects.create(
            product=product,
            author_name='Test User',
            author_email='test@example.com',
            rating=5,
            content='Great product'
        )
        
        helpfulness = ReviewHelpfulness.objects.create(
            review=review,
            is_helpful=False
        )
        assert str(helpfulness) == f"False - {review}"
