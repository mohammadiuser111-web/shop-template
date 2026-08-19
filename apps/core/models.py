"""
Core models for shop-template project.
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import json
import uuid


class ThemeConfig(models.Model):
    """
    Model for storing theme configuration.
    This allows changing the appearance of the site without touching code.
    """
    name = models.CharField(max_length=100, verbose_name='Name')
    config_json = models.JSONField(verbose_name='Configuration JSON', default=dict)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Theme Configuration'
        verbose_name_plural = 'Theme Configurations'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Validate JSON configuration before saving."""
        try:
            # Validate that config_json has required fields
            config = self.config_json
            if not isinstance(config, dict):
                raise ValidationError("Configuration must be a JSON object")
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON configuration")
        super().save(*args, **kwargs)

    @classmethod
    def get_active_config(cls):
        """Get the currently active theme configuration."""
        return cls.objects.filter(is_active=True).first()


class SiteSetting(models.Model):
    """
    Model for storing individual site settings as key-value pairs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, verbose_name='Key')
    value = models.TextField(verbose_name='Value', blank=True)
    description = models.TextField(verbose_name='Description', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'
        ordering = ['sort_order', 'key']
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class SiteSettings(models.Model):
    """
    Model for storing general site settings (singleton pattern).
    """
    SINGLETONE = True
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site_name = models.CharField(max_length=100, verbose_name='Site Name', default='Shop Template')
    site_description = models.TextField(verbose_name='Site Description', blank=True)
    site_logo = models.ImageField(upload_to='logos/', verbose_name='Site Logo', blank=True, null=True)
    site_favicon = models.ImageField(upload_to='favicons/', verbose_name='Site Favicon', blank=True, null=True)
    contact_email = models.EmailField(verbose_name='Contact Email', blank=True)
    contact_phone = models.CharField(max_length=20, verbose_name='Contact Phone', blank=True)
    address = models.TextField(verbose_name='Address', blank=True)
    
    # Social media links
    facebook_url = models.URLField(verbose_name='Facebook URL', blank=True)
    twitter_url = models.URLField(verbose_name='Twitter URL', blank=True)
    instagram_url = models.URLField(verbose_name='Instagram URL', blank=True)
    telegram_url = models.URLField(verbose_name='Telegram URL', blank=True)
    linkedin_url = models.URLField(verbose_name='LinkedIn URL', blank=True)
    
    # Financial settings
    currency = models.CharField(max_length=3, verbose_name='Currency', default='IRR')
    currency_symbol = models.CharField(max_length=5, verbose_name='Currency Symbol', default='تومان')
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Default Tax Rate', default=0.09)
    
    # SEO settings
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', blank=True)
    meta_keywords = models.TextField(verbose_name='Meta Keywords', blank=True)
    
    # Maintenance mode
    maintenance_mode = models.BooleanField(default=False, verbose_name='Maintenance Mode')
    maintenance_message = models.TextField(verbose_name='Maintenance Message', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)."""
        if self.SINGLETONE:
            self.pk = 1
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        return cls.objects.first()


class SocialLink(models.Model):
    """
    Model for storing social media links.
    """
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('whatsapp', 'WhatsApp'),
        ('tiktok', 'TikTok'),
        ('snapchat', 'Snapchat'),
        ('pinterest', 'Pinterest'),
        ('reddit', 'Reddit'),
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name='Platform')
    url = models.URLField(verbose_name='URL')
    icon = models.CharField(max_length=50, verbose_name='Icon Class', default='fa-link')
    title = models.CharField(max_length=50, verbose_name='Title', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    is_new_window = models.BooleanField(default=True, verbose_name='Open in New Window')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Social Link'
        verbose_name_plural = 'Social Links'
        ordering = ['sort_order', 'platform']
    
    def __str__(self):
        return f"{self.get_platform_display()} - {self.url}"
    
    def save(self, *args, **kwargs):
        """Auto-set title and icon based on platform."""
        if not self.title:
            self.title = self.get_platform_display()
        if self.icon == 'fa-link':
            platform_icons = {
                'facebook': 'fab fa-facebook',
                'twitter': 'fab fa-twitter',
                'instagram': 'fab fa-instagram',
                'telegram': 'fab fa-telegram',
                'linkedin': 'fab fa-linkedin',
                'youtube': 'fab fa-youtube',
                'whatsapp': 'fab fa-whatsapp',
                'tiktok': 'fab fa-tiktok',
                'snapchat': 'fab fa-snapchat-ghost',
                'pinterest': 'fab fa-pinterest',
                'reddit': 'fab fa-reddit-alien',
                'github': 'fab fa-github',
                'gitlab': 'fab fa-gitlab',
                'custom': 'fa-link',
            }
            self.icon = platform_icons.get(self.platform, 'fa-link')
        super().save(*args, **kwargs)


class ContactInfo(models.Model):
    """
    Model for storing contact information.
    """
    INFO_TYPES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('mobile', 'Mobile'),
        ('fax', 'Fax'),
        ('address', 'Address'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=INFO_TYPES, verbose_name='Type')
    value = models.CharField(max_length=200, verbose_name='Value')
    icon = models.CharField(max_length=50, verbose_name='Icon Class', default='fa-info-circle')
    label = models.CharField(max_length=50, verbose_name='Label', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Contact Info'
        verbose_name_plural = 'Contact Info'
        ordering = ['sort_order', 'type']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.value}"


class Menu(models.Model):
    """
    Model for storing navigation menus.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Name')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MenuItem(models.Model):
    """
    Model for storing menu items.
    """
    TARGET_CHOICES = [
        ('_self', 'Same Window'),
        ('_blank', 'New Window'),
        ('_parent', 'Parent Frame'),
        ('_top', 'Top Frame'),
    ]
    
    ITEM_TYPES = [
        ('url', 'URL'),
        ('page', 'Page'),
        ('product', 'Product'),
        ('category', 'Category'),
        ('blog_post', 'Blog Post'),
        ('blog_category', 'Blog Category'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Menu'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name='Parent'
    )
    
    title = models.CharField(max_length=100, verbose_name='Title')
    url = models.CharField(max_length=500, verbose_name='URL', blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='url', verbose_name='Item Type')
    
    # Related objects (for non-URL types)
    page = models.ForeignKey(
        'Page',
        on_delete=models.SET_NULL,
        related_name='menu_items',
        null=True,
        blank=True,
        verbose_name='Page'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        related_name='menu_items',
        null=True,
        blank=True,
        verbose_name='Product'
    )
    category = models.ForeignKey(
        'products.Category',
        on_delete=models.SET_NULL,
        related_name='menu_items',
        null=True,
        blank=True,
        verbose_name='Category'
    )
    blog_post = models.ForeignKey(
        'blog.Article',
        on_delete=models.SET_NULL,
        related_name='menu_items',
        null=True,
        blank=True,
        verbose_name='Blog Post'
    )
    blog_category = models.ForeignKey(
        'blog.BlogCategory',
        on_delete=models.SET_NULL,
        related_name='menu_items',
        null=True,
        blank=True,
        verbose_name='Blog Category'
    )
    
    icon = models.CharField(max_length=50, verbose_name='Icon Class', blank=True)
    target = models.CharField(max_length=10, choices=TARGET_CHOICES, default='_self', verbose_name='Target')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    css_class = models.CharField(max_length=100, verbose_name='CSS Class', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['menu__sort_order', 'sort_order', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.menu.name})"
    
    def get_url(self):
        """Get the actual URL for this menu item."""
        if self.url:
            return self.url
        
        if self.item_type == 'page' and self.page:
            return f'/page/{self.page.slug}/'
        elif self.item_type == 'product' and self.product:
            return f'/products/{self.product.slug}/'
        elif self.item_type == 'category' and self.category:
            return f'/products/category/{self.category.slug}/'
        elif self.item_type == 'blog_post' and self.blog_post:
            return f'/blog/{self.blog_post.slug}/'
        elif self.item_type == 'blog_category' and self.blog_category:
            return f'/blog/category/{self.blog_category.slug}/'
        
        return self.url


class Page(models.Model):
    """
    Model for storing custom pages.
    """
    TEMPLATE_CHOICES = [
        ('pages/default.html', 'Default'),
        ('pages/full_width.html', 'Full Width'),
        ('pages/sidebar_left.html', 'Sidebar Left'),
        ('pages/sidebar_right.html', 'Sidebar Right'),
        ('pages/contact.html', 'Contact Form'),
        ('pages/about.html', 'About Page'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name='Title')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    content = models.TextField(verbose_name='Content', blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', blank=True)
    meta_keywords = models.TextField(verbose_name='Meta Keywords', blank=True)
    
    # Display settings
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    is_published = models.BooleanField(default=True, verbose_name='Is Published')
    is_featured = models.BooleanField(default=False, verbose_name='Is Featured')
    template_name = models.CharField(
        max_length=100,
        choices=TEMPLATE_CHOICES,
        default='pages/default.html',
        verbose_name='Template'
    )
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    # Access control
    require_login = models.BooleanField(default=False, verbose_name='Require Login')
    allowed_groups = models.ManyToManyField(
        'auth.Group',
        related_name='allowed_pages',
        verbose_name='Allowed Groups',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    published_at = models.DateTimeField(verbose_name='Published At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        ordering = ['-is_featured', '-sort_order', 'title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title."""
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at if not set and is_published
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get absolute URL for this page."""
        return f'/page/{self.slug}/'


class ActivityLog(models.Model):
    """
    Model for tracking user activities in the admin panel.
    """
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('VIEW', 'View'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='User'
    )
    action = models.CharField(max_length=10, choices=ACTION_TYPES, verbose_name='Action')
    model_name = models.CharField(max_length=100, verbose_name='Model Name', blank=True)
    object_id = models.PositiveIntegerField(verbose_name='Object ID', null=True, blank=True)
    object_repr = models.CharField(max_length=200, verbose_name='Object Representation', blank=True)
    description = models.TextField(verbose_name='Description', blank=True)
    ip_address = models.GenericIPAddressField(verbose_name='IP Address', null=True, blank=True)
    user_agent = models.TextField(verbose_name='User Agent', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['model_name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} - {self.created_at}"


class ContactMessage(models.Model):
    """
    Model for contact form messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Contact information
    name = models.CharField(max_length=200, verbose_name='Name')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Phone', blank=True)
    
    # Message content
    subject = models.CharField(max_length=300, verbose_name='Subject')
    message = models.TextField(verbose_name='Message')
    department = models.CharField(max_length=100, verbose_name='Department', blank=True)
    
    # User association
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='contact_messages',
        null=True,
        blank=True,
        verbose_name='User'
    )
    
    # Tracking
    ip_address = models.GenericIPAddressField(verbose_name='IP Address', null=True, blank=True)
    is_read = models.BooleanField(default=False, verbose_name='Is Read')
    is_archived = models.BooleanField(default=False, verbose_name='Is Archived')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.name}"
