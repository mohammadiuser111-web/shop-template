"""
Review models for shop-template project.
"""
from django.db import models
from django.conf import settings
import uuid


class Review(models.Model):
    """
    Model for product reviews.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Product'
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        related_name='reviews',
        null=True,
        blank=True,
        verbose_name='Variant'
    )
    
    # Author
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='reviews',
        null=True,
        blank=True,
        verbose_name='User'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        related_name='reviews',
        null=True,
        blank=True,
        verbose_name='Order'
    )
    order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.SET_NULL,
        related_name='reviews',
        null=True,
        blank=True,
        verbose_name='Order Item'
    )
    
    # Author information (for guest reviews)
    author_name = models.CharField(max_length=200, verbose_name='Author Name')
    author_email = models.EmailField(verbose_name='Author Email')
    
    # Rating
    rating = models.PositiveSmallIntegerField(
        verbose_name='Rating',
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]
    )
    
    # Content
    title = models.CharField(max_length=200, verbose_name='Title', blank=True)
    content = models.TextField(verbose_name='Content')
    pros = models.TextField(verbose_name='Pros', blank=True)
    cons = models.TextField(verbose_name='Cons', blank=True)
    
    # Media
    images = models.ManyToManyField(
        'ReviewImage',
        related_name='reviews',
        verbose_name='Images',
        blank=True
    )
    videos = models.ManyToManyField(
        'ReviewVideo',
        related_name='reviews',
        verbose_name='Videos',
        blank=True
    )
    
    # Status
    is_approved = models.BooleanField(default=False, verbose_name='Is Approved')
    is_verified_purchase = models.BooleanField(default=False, verbose_name='Is Verified Purchase')
    is_recommended = models.BooleanField(default=False, verbose_name='Is Recommended')
    
    # Helpfulness
    helpful_count = models.PositiveIntegerField(default=0, verbose_name='Helpful Count')
    not_helpful_count = models.PositiveIntegerField(default=0, verbose_name='Not Helpful Count')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    approved_at = models.DateTimeField(verbose_name='Approved At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['variant']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.rating} star review for {self.product.name}"
    
    def get_author_name(self):
        """Get author display name."""
        if self.user:
            return self.user.get_full_name() or self.user.phone_number or self.user.email
        return self.author_name
    
    def get_rating_display(self):
        """Get rating as stars."""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    def get_helpfulness_percentage(self):
        """Calculate helpfulness percentage."""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0
        return (self.helpful_count / total) * 100
    
    def approve(self):
        """Approve the review."""
        self.is_approved = True
        self.approved_at = models.DateTimeField(auto_now_add=True)
        self.save()
    
    def mark_as_verified(self):
        """Mark as verified purchase."""
        self.is_verified_purchase = True
        self.save()


class ReviewImage(models.Model):
    """
    Model for review images.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='reviews/', verbose_name='Image')
    caption = models.CharField(max_length=200, verbose_name='Caption', blank=True)
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Review Image'
        verbose_name_plural = 'Review Images'
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Image {self.id}"


class ReviewVideo(models.Model):
    """
    Model for review videos.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.FileField(upload_to='reviews/videos/', verbose_name='Video')
    thumbnail = models.ImageField(upload_to='reviews/thumbnails/', verbose_name='Thumbnail', null=True, blank=True)
    caption = models.CharField(max_length=200, verbose_name='Caption', blank=True)
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Review Video'
        verbose_name_plural = 'Review Videos'
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Video {self.id}"


class ReviewComment(models.Model):
    """
    Model for review comments (admin responses).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Review'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='review_comments',
        null=True,
        blank=True,
        verbose_name='User'
    )
    content = models.TextField(verbose_name='Content')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Review Comment'
        verbose_name_plural = 'Review Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on review {self.review.id}"


class ReviewHelpfulness(models.Model):
    """
    Model for tracking review helpfulness votes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpfulness_votes',
        verbose_name='Review'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='helpfulness_votes',
        null=True,
        blank=True,
        verbose_name='User'
    )
    is_helpful = models.BooleanField(verbose_name='Is Helpful')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Review Helpfulness'
        verbose_name_plural = 'Review Helpfulness'
        unique_together = [['review', 'user']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.is_helpful} - {self.review}"
