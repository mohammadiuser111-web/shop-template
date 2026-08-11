"""
Signals for dashboard_admin app.
Track admin activities and automatic logging.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.admin.signals import log_addition, log_change, log_deletion
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import AdminActivity, AdminUserSettings, AdminSettings
from apps.accounts.models import User


@receiver(post_save, sender=User)
def track_user_creation(sender, instance, created, **kwargs):
    """Track user creation and updates."""
    if created:
        AdminActivity.objects.create(
            action='create',
            model_name='User',
            object_id=instance.pk,
            object_repr=str(instance),
            description=f'کاربر جدید با نام کاربری {instance.username} ایجاد شد'
        )
    else:
        # Track field changes
        if not kwargs.get('raw', False):
            try:
                old_instance = User.objects.get(pk=instance.pk)
                changes = {}
                
                for field in ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']:
                    old_value = getattr(old_instance, field)
                    new_value = getattr(instance, field)
                    if old_value != new_value:
                        changes[field] = {
                            'old': str(old_value),
                            'new': str(new_value)
                        }
                
                if changes:
                    AdminActivity.objects.create(
                        action='update',
                        model_name='User',
                        object_id=instance.pk,
                        object_repr=str(instance),
                        description=f'بروزرسانی کاربر {instance.username}',
                        changes=changes
                    )
            except User.DoesNotExist:
                pass


@receiver(post_delete, sender=User)
def track_user_deletion(sender, instance, **kwargs):
    """Track user deletion."""
    AdminActivity.objects.create(
        action='delete',
        model_name='User',
        object_id=instance.pk,
        object_repr=str(instance),
        description=f'کاربر {instance.username} حذف شد'
    )


# Generic signal handlers for all models
MODELS_TO_TRACK = [
    'products.Product',
    'products.Category',
    'products.Brand',
    'orders.Order',
    'orders.OrderItem',
    'payments.Payment',
    'shipping.ShippingMethod',
    'discounts.Coupon',
    'discounts.Discount',
    'inventory.Inventory',
    'blog.Post',
    'blog.Category',
    'reviews.Review',
    'ads.AdSpace',
    'ads.AdBanner',
    'support.Ticket',
    'support.TicketMessage',
]


def get_model_from_string(model_string):
    """Get model class from string."""
    try:
        app_label, model_name = model_string.split('.')
        from django.apps import apps
        return apps.get_model(app_label, model_name)
    except (ValueError, LookupError):
        return None


@receiver(post_save)
def track_model_save(sender, instance, created, **kwargs):
    """Track model creation and updates."""
    # Skip if this is a raw save (e.g., during migrations)
    if kwargs.get('raw', False):
        return
    
    # Skip if this is one of our own models
    if sender.__name__ in ['AdminActivity', 'AdminUserSettings', 'AdminSettings']:
        return
    
    # Check if this model should be tracked
    model_string = f'{sender._meta.app_label}.{sender._meta.model_name}'
    if model_string not in MODELS_TO_TRACK:
        return
    
    action = 'create' if created else 'update'
    
    # For updates, track changes
    changes = {}
    if not created:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            for field in sender._meta.fields:
                if hasattr(field, 'name'):
                    old_value = getattr(old_instance, field.name)
                    new_value = getattr(instance, field.name)
                    if old_value != new_value:
                        changes[field.name] = {
                            'old': str(old_value) if old_value is not None else 'None',
                            'new': str(new_value) if new_value is not None else 'None'
                        }
        except sender.DoesNotExist:
            pass
    
    AdminActivity.objects.create(
        action=action,
        model_name=model_string,
        object_id=instance.pk,
        object_repr=str(instance),
        description=f'{action} {sender._meta.verbose_name} {instance}',
        changes=changes if changes else {}
    )


@receiver(post_delete)
def track_model_delete(sender, instance, **kwargs):
    """Track model deletion."""
    # Skip if this is a raw delete
    if kwargs.get('raw', False):
        return
    
    # Skip if this is one of our own models
    if sender.__name__ in ['AdminActivity', 'AdminUserSettings', 'AdminSettings']:
        return
    
    # Check if this model should be tracked
    model_string = f'{sender._meta.app_label}.{sender._meta.model_name}'
    if model_string not in MODELS_TO_TRACK:
        return
    
    AdminActivity.objects.create(
        action='delete',
        model_name=model_string,
        object_id=instance.pk,
        object_repr=str(instance),
        description=f'delete {sender._meta.verbose_name} {instance}'
    )


@receiver(user_logged_in)
def track_user_login(sender, request, user, **kwargs):
    """Track user login."""
    if user.is_staff:
        AdminActivity.objects.create(
            user=user,
            action='login',
            model_name='User',
            object_id=user.pk,
            object_repr=str(user),
            description=f'ورود کاربر {user.username}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )


@receiver(user_logged_out)
def track_user_logout(sender, request, user, **kwargs):
    """Track user logout."""
    if user and user.is_staff:
        AdminActivity.objects.create(
            user=user,
            action='logout',
            model_name='User',
            object_id=user.pk,
            object_repr=str(user),
            description=f'خروج کاربر {user.username}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )


@receiver(log_addition)
def track_admin_log_addition(sender, **kwargs):
    """Track admin log additions."""
    log_entry = kwargs.get('log_entry')
    if log_entry and log_entry.user and log_entry.user.is_staff:
        content_type = log_entry.content_type
        model_string = f'{content_type.app_label}.{content_type.model}'
        
        AdminActivity.objects.create(
            user=log_entry.user,
            action='create',
            model_name=model_string,
            object_id=log_entry.object_id,
            object_repr=log_entry.object_repr,
            description=f'ایجاد {content_type.model} از طریق پنل مدیریت',
            ip_address=log_entry.ip if hasattr(log_entry, 'ip') else '',
            user_agent=''
        )


@receiver(log_change)
def track_admin_log_change(sender, **kwargs):
    """Track admin log changes."""
    log_entry = kwargs.get('log_entry')
    if log_entry and log_entry.user and log_entry.user.is_staff:
        content_type = log_entry.content_type
        model_string = f'{content_type.app_label}.{content_type.model}'
        
        AdminActivity.objects.create(
            user=log_entry.user,
            action='update',
            model_name=model_string,
            object_id=log_entry.object_id,
            object_repr=log_entry.object_repr,
            description=f'بروزرسانی {content_type.model} از طریق پنل مدیریت',
            changes={'admin_change': True},
            ip_address=log_entry.ip if hasattr(log_entry, 'ip') else '',
            user_agent=''
        )


@receiver(log_deletion)
def track_admin_log_deletion(sender, **kwargs):
    """Track admin log deletions."""
    log_entry = kwargs.get('log_entry')
    if log_entry and log_entry.user and log_entry.user.is_staff:
        content_type = log_entry.content_type
        model_string = f'{content_type.app_label}.{content_type.model}'
        
        AdminActivity.objects.create(
            user=log_entry.user,
            action='delete',
            model_name=model_string,
            object_id=log_entry.object_id,
            object_repr=log_entry.object_repr,
            description=f'حذف {content_type.model} از طریق پنل مدیریت',
            ip_address=log_entry.ip if hasattr(log_entry, 'ip') else '',
            user_agent=''
        )


@receiver(pre_save, sender=AdminUserSettings)
def update_user_settings(sender, instance, **kwargs):
    """Update user settings before save."""
    if not instance.pk:
        # New instance - set default dashboard if not set
        if not instance.dashboard:
            default_dashboard = AdminDashboard.objects.filter(is_default=True).first()
            if default_dashboard:
                instance.dashboard = default_dashboard


@receiver(post_save, sender=AdminSettings)
def update_global_settings(sender, instance, created, **kwargs):
    """Update global settings."""
    if created:
        # First settings instance - create default dashboard
        if not AdminDashboard.objects.exists():
            AdminDashboard.objects.create(
                name='داشبورد پیش‌فرض',
                code='default',
                description='داشبورد پیش‌فرض سیستم',
                layout={
                    'widgets': [],
                    'columns': 2,
                },
                is_default=True,
                is_active=True
            )
