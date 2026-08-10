"""
Blog models for shop-template project.
"""
from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class BlogCategory(models.Model):
    """
    Model for blog categories.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name='Parent Category'
    )
    image = models.ImageField(upload_to='blog/categories/', verbose_name='Image', null=True, blank=True)
    icon = models.CharField(max_length=50, verbose_name='Icon', blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', blank=True)
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        ordering = ['parent__sort_order', 'sort_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    """
    Model for blog tags.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Name')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    color = models.CharField(max_length=20, verbose_name='Color', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:tag', kwargs={'slug': self.slug})


class Article(models.Model):
    """
    Model for blog articles.
    """
    ARTICLE_STATUS = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300, verbose_name='Title')
    slug = models.SlugField(max_length=300, unique=True, verbose_name='Slug')
    
    # Content
    excerpt = models.TextField(verbose_name='Excerpt', blank=True)
    content = models.TextField(verbose_name='Content')
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='articles',
        null=True,
        blank=True,
        verbose_name='Author'
    )
    
    # Categories and Tags
    categories = models.ManyToManyField(
        BlogCategory,
        related_name='articles',
        verbose_name='Categories',
        blank=True
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='articles',
        verbose_name='Tags',
        blank=True
    )
    
    # Featured image
    featured_image = models.ImageField(upload_to='blog/articles/', verbose_name='Featured Image', null=True, blank=True)
    featured_image_caption = models.CharField(max_length=300, verbose_name='Featured Image Caption', blank=True)
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=ARTICLE_STATUS, default='draft', verbose_name='Status')
    is_featured = models.BooleanField(default=False, verbose_name='Is Featured')
    is_popular = models.BooleanField(default=False, verbose_name='Is Popular')
    allow_comments = models.BooleanField(default=True, verbose_name='Allow Comments')
    
    # Publication dates
    published_at = models.DateTimeField(verbose_name='Published At', null=True, blank=True)
    scheduled_at = models.DateTimeField(verbose_name='Scheduled At', null=True, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', blank=True)
    meta_keywords = models.TextField(verbose_name='Meta Keywords', blank=True)
    canonical_url = models.URLField(verbose_name='Canonical URL', blank=True)
    
    # View count
    view_count = models.PositiveIntegerField(default=0, verbose_name='View Count')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['published_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:article_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        """Generate slug from title if not provided."""
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def increment_view_count(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def get_author_name(self):
        """Get author display name."""
        if self.author:
            return self.author.get_full_name() or self.author.phone_number or self.author.email
        return 'Unknown'
    
    def get_category_names(self):
        """Get comma-separated category names."""
        return ', '.join(self.categories.values_list('name', flat=True))
    
    def get_tag_names(self):
        """Get comma-separated tag names."""
        return ', '.join(self.tags.values_list('name', flat=True))
    
    def is_published(self):
        """Check if article is published."""
        return self.status == 'published'


class ArticleImage(models.Model):
    """
    Model for article images (gallery).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Article'
    )
    image = models.ImageField(upload_to='blog/articles/', verbose_name='Image')
    caption = models.CharField(max_length=300, verbose_name='Caption', blank=True)
    alt_text = models.CharField(max_length=200, verbose_name='Alt Text', blank=True)
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Article Image'
        verbose_name_plural = 'Article Images'
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.article.title} - Image {self.sort_order}"


class ArticleRelated(models.Model):
    """
    Through model for article relationships.
    """
    from_article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='related_from',
        verbose_name='From Article'
    )
    to_article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='related_to',
        verbose_name='To Article'
    )
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Related Article'
        verbose_name_plural = 'Related Articles'
        unique_together = [['from_article', 'to_article']]
        ordering = ['sort_order']
    
    def __str__(self):
        return f"{self.from_article.title} -> {self.to_article.title}"


class Comment(models.Model):
    """
    Model for article comments.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Article'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        verbose_name='Parent Comment'
    )
    
    # Author
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='comments',
        null=True,
        blank=True,
        verbose_name='User'
    )
    author_name = models.CharField(max_length=200, verbose_name='Author Name')
    author_email = models.EmailField(verbose_name='Author Email')
    author_website = models.URLField(verbose_name='Author Website', blank=True)
    author_ip = models.GenericIPAddressField(verbose_name='Author IP', null=True, blank=True)
    
    # Content
    content = models.TextField(verbose_name='Content')
    
    # Status
    is_approved = models.BooleanField(default=False, verbose_name='Is Approved')
    is_spam = models.BooleanField(default=False, verbose_name='Is Spam')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    approved_at = models.DateTimeField(verbose_name='Approved At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.article.title}"
    
    def get_author_name(self):
        """Get author display name."""
        if self.user:
            return self.user.get_full_name() or self.user.phone_number or self.user.email
        return self.author_name
    
    def get_replies(self):
        """Get all replies to this comment."""
        return self.replies.filter(is_approved=True)
    
    def has_replies(self):
        """Check if comment has replies."""
        return self.replies.exists()
    
    def approve(self):
        """Approve the comment."""
        self.is_approved = True
        self.approved_at = models.DateTimeField(auto_now_add=True)
        self.save()
    
    def mark_as_spam(self):
        """Mark comment as spam."""
        self.is_spam = True
        self.save()


class CommentRating(models.Model):
    """
    Model for comment ratings (upvote/downvote).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Comment'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='comment_ratings',
        null=True,
        blank=True,
        verbose_name='User'
    )
    rating = models.SmallIntegerField(verbose_name='Rating')  # 1 = upvote, -1 = downvote
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Comment Rating'
        verbose_name_plural = 'Comment Ratings'
        unique_together = [['comment', 'user']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rating} - {self.comment}"
