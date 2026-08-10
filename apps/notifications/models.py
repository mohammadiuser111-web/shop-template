"""
Notification models for shop-template project.
"""
from django.db import models
from django.conf import settings
import uuid


class Notification(models.Model):
    """
    Model for user notifications.
    """
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('order', 'Order Update'),
        ('payment', 'Payment Update'),
        ('shipping', 'Shipping Update'),
        ('promotion', 'Promotion'),
        ('message', 'Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='User'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='Type')
    
    # Content
    title = models.CharField(max_length=200, verbose_name='Title')
    message = models.TextField(verbose_name='Message')
    
    # URL
    url = models.URLField(verbose_name='URL', blank=True)
    
    # Related object
    related_object_type = models.CharField(max_length=100, verbose_name='Related Object Type', blank=True)
    related_object_id = models.PositiveIntegerField(verbose_name='Related Object ID', null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False, verbose_name='Is Read')
    is_archived = models.BooleanField(default=False, verbose_name='Is Archived')
    
    # Priority
    priority = models.PositiveSmallIntegerField(default=0, verbose_name='Priority')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    read_at = models.DateTimeField(verbose_name='Read At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.read_at = models.DateTimeField(auto_now_add=True)
        self.save()
    
    def mark_as_archived(self):
        """Mark notification as archived."""
        self.is_archived = True
        self.save()
    
    def get_related_object(self):
        """Get the related object if available."""
        if self.related_object_type and self.related_object_id:
            from django.apps import apps
            try:
                model = apps.get_model(self.related_object_type)
                return model.objects.get(pk=self.related_object_id)
            except (LookupError, model.DoesNotExist):
                pass
        return None


class NotificationTemplate(models.Model):
    """
    Model for notification templates.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=100, unique=True, verbose_name='Code')
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES, 
                                         default='info', verbose_name='Notification Type')
    
    # Content
    title_template = models.CharField(max_length=300, verbose_name='Title Template')
    message_template = models.TextField(verbose_name='Message Template')
    
    # URL template
    url_template = models.URLField(verbose_name='URL Template', blank=True)
    
    # Related model
    related_model = models.CharField(max_length=100, verbose_name='Related Model', blank=True)
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def render(self, context):
        """Render notification with context."""
        from django.template import Template, Context
        
        title_template = Template(self.title_template)
        message_template = Template(self.message_template)
        url_template = Template(self.url_template) if self.url_template else None
        
        django_context = Context(context)
        
        title = title_template.render(django_context)
        message = message_template.render(django_context)
        url = url_template.render(django_context) if url_template else ''
        
        return {
            'title': title,
            'message': message,
            'url': url,
        }


class EmailNotification(models.Model):
    """
    Model for email notifications.
    """
    EMAIL_TYPES = [
        ('order_confirmation', 'Order Confirmation'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('payment_received', 'Payment Received'),
        ('reset_password', 'Reset Password'),
        ('welcome', 'Welcome'),
        ('newsletter', 'Newsletter'),
        ('promotion', 'Promotion'),
        ('support', 'Support'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPES, verbose_name='Email Type')
    
    # Recipient
    to_email = models.EmailField(verbose_name='To Email')
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='email_notifications',
        null=True,
        blank=True,
        verbose_name='To User'
    )
    
    # Content
    subject = models.CharField(max_length=300, verbose_name='Subject')
    body = models.TextField(verbose_name='Body')
    body_html = models.TextField(verbose_name='Body HTML', blank=True)
    
    # Status
    is_sent = models.BooleanField(default=False, verbose_name='Is Sent')
    send_attempts = models.PositiveSmallIntegerField(default=0, verbose_name='Send Attempts')
    
    # Error information
    error_message = models.TextField(verbose_name='Error Message', blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    sent_at = models.DateTimeField(verbose_name='Sent At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Email Notification'
        verbose_name_plural = 'Email Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['to_email']),
            models.Index(fields=['is_sent']),
        ]
    
    def __str__(self):
        return f"{self.email_type} - {self.to_email}"


class PushNotification(models.Model):
    """
    Model for push notifications (web push, mobile push).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_notifications',
        verbose_name='User'
    )
    
    # Content
    title = models.CharField(max_length=200, verbose_name='Title')
    body = models.TextField(verbose_name='Body')
    
    # Data payload
    data = models.JSONField(verbose_name='Data', default=dict, blank=True)
    
    # URL
    url = models.URLField(verbose_name='URL', blank=True)
    
    # Status
    is_sent = models.BooleanField(default=False, verbose_name='Is Sent')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    sent_at = models.DateTimeField(verbose_name='Sent At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Push Notification'
        verbose_name_plural = 'Push Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user}"


class SMSNotification(models.Model):
    """
    Model for SMS notifications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, verbose_name='Phone Number')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='sms_notifications',
        null=True,
        blank=True,
        verbose_name='User'
    )
    
    # Content
    message = models.TextField(verbose_name='Message')
    
    # Status
    is_sent = models.BooleanField(default=False, verbose_name='Is Sent')
    send_attempts = models.PositiveSmallIntegerField(default=0, verbose_name='Send Attempts')
    
    # Error information
    error_message = models.TextField(verbose_name='Error Message', blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    sent_at = models.DateTimeField(verbose_name='Sent At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'SMS Notification'
        verbose_name_plural = 'SMS Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['is_sent']),
        ]
    
    def __str__(self):
        return f"SMS to {self.phone_number}"


class DeviceToken(models.Model):
    """
    Model for storing device tokens for push notifications.
    """
    DEVICE_TYPES = [
        ('web', 'Web'),
        ('android', 'Android'),
        ('ios', 'iOS'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens',
        verbose_name='User'
    )
    token = models.TextField(verbose_name='Token')
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES, verbose_name='Device Type')
    device_name = models.CharField(max_length=200, verbose_name='Device Name', blank=True)
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Device Token'
        verbose_name_plural = 'Device Tokens'
        unique_together = [['user', 'token']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.device_type} - {self.device_name}"
