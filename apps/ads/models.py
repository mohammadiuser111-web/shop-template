"""
Advertisement models for shop-template project.
"""
from django.db import models
from django.conf import settings
import uuid


class AdSlot(models.Model):
    """
    Model for advertisement slots/positions on the site.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=100, unique=True, verbose_name='Code')
    description = models.TextField(verbose_name='Description', blank=True)
    
    # Dimensions
    width = models.PositiveIntegerField(verbose_name='Width (px)', null=True, blank=True)
    height = models.PositiveIntegerField(verbose_name='Height (px)', null=True, blank=True)
    
    # Position
    is_responsive = models.BooleanField(default=True, verbose_name='Is Responsive')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Ad Slot'
        verbose_name_plural = 'Ad Slots'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_current_ad(self):
        """Get the currently active ad for this slot."""
        from django.utils import timezone
        return self.ads.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).order_by('-priority', '-created_at').first()


class Advertisement(models.Model):
    """
    Model for advertisements.
    """
    AD_TYPES = [
        ('image', 'Image'),
        ('html', 'HTML'),
        ('script', 'JavaScript'),
        ('video', 'Video'),
    ]
    
    TARGET_TYPES = [
        ('blank', 'New Window/Tab'),
        ('self', 'Same Window'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    
    # Slot
    slot = models.ForeignKey(
        AdSlot,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name='Ad Slot'
    )
    
    # Content
    ad_type = models.CharField(max_length=20, choices=AD_TYPES, default='image', verbose_name='Ad Type')
    
    # For image ads
    image = models.ImageField(upload_to='ads/', verbose_name='Image', null=True, blank=True)
    image_alt = models.CharField(max_length=200, verbose_name='Image Alt Text', blank=True)
    
    # For HTML/script ads
    html_content = models.TextField(verbose_name='HTML Content', blank=True)
    script_content = models.TextField(verbose_name='Script Content', blank=True)
    
    # For video ads
    video_url = models.URLField(verbose_name='Video URL', blank=True)
    video_embed_code = models.TextField(verbose_name='Video Embed Code', blank=True)
    
    # Link
    url = models.URLField(verbose_name='URL', blank=True)
    target = models.CharField(max_length=10, choices=TARGET_TYPES, default='blank', verbose_name='Target')
    
    # Display settings
    title = models.CharField(max_length=200, verbose_name='Title', blank=True)
    description = models.TextField(verbose_name='Description', blank=True)
    
    # Timing
    start_date = models.DateTimeField(verbose_name='Start Date', null=True, blank=True)
    end_date = models.DateTimeField(verbose_name='End Date', null=True, blank=True)
    
    # Priority and status
    priority = models.IntegerField(default=0, verbose_name='Priority')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    # Statistics
    impression_count = models.PositiveIntegerField(default=0, verbose_name='Impression Count')
    click_count = models.PositiveIntegerField(default=0, verbose_name='Click Count')
    
    # User
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_ads',
        null=True,
        blank=True,
        verbose_name='Created By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['slot']),
            models.Index(fields=['is_active']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.slot.name}"
    
    def is_valid(self):
        """Check if ad is currently valid."""
        from django.utils import timezone
        now = timezone.now()
        return (self.is_active and 
                (self.start_date is None or self.start_date <= now) and
                (self.end_date is None or self.end_date >= now))
    
    def increment_impressions(self):
        """Increment impression count."""
        self.impression_count += 1
        self.save(update_fields=['impression_count'])
    
    def increment_clicks(self):
        """Increment click count."""
        self.click_count += 1
        self.save(update_fields=['click_count'])
    
    def get_ctr(self):
        """Calculate Click-Through Rate."""
        if self.impression_count == 0:
            return 0
        return (self.click_count / self.impression_count) * 100


class AdImpression(models.Model):
    """
    Model for tracking ad impressions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ad = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name='impressions',
        verbose_name='Advertisement'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='ad_impressions',
        null=True,
        blank=True,
        verbose_name='User'
    )
    ip_address = models.GenericIPAddressField(verbose_name='IP Address', null=True, blank=True)
    user_agent = models.TextField(verbose_name='User Agent', blank=True)
    referrer = models.URLField(verbose_name='Referrer', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Ad Impression'
        verbose_name_plural = 'Ad Impressions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ad']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Impression for {self.ad.name}"


class AdClick(models.Model):
    """
    Model for tracking ad clicks.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ad = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name='clicks',
        verbose_name='Advertisement'
    )
    impression = models.ForeignKey(
        AdImpression,
        on_delete=models.SET_NULL,
        related_name='click',
        null=True,
        blank=True,
        verbose_name='Impression'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='ad_clicks',
        null=True,
        blank=True,
        verbose_name='User'
    )
    ip_address = models.GenericIPAddressField(verbose_name='IP Address', null=True, blank=True)
    user_agent = models.TextField(verbose_name='User Agent', blank=True)
    referrer = models.URLField(verbose_name='Referrer', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Ad Click'
        verbose_name_plural = 'Ad Clicks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ad']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Click for {self.ad.name}"
