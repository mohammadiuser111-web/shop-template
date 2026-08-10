"""
Core models for shop-template project.
"""
from django.db import models
from django.core.exceptions import ValidationError
import json


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


class SiteSettings(models.Model):
    """
    Model for storing general site settings.
    """
    SINGLETONE = True
    
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
