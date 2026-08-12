"""
Signals for ads app.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import AdSlot, Advertisement
from .services import AdService


@receiver(post_save, sender=AdSlot)
def clear_slot_cache(sender, instance, created, **kwargs):
    """Clear cache when a slot is saved."""
    AdService.clear_ad_cache(slot_code=instance.code)


@receiver(post_delete, sender=AdSlot)
def clear_deleted_slot_cache(sender, instance, **kwargs):
    """Clear cache when a slot is deleted."""
    AdService.clear_ad_cache(slot_code=instance.code)


@receiver(post_save, sender=Advertisement)
def clear_ad_cache(sender, instance, created, **kwargs):
    """Clear cache when an ad is saved."""
    if instance.slot:
        AdService.clear_ad_cache(slot_code=instance.slot.code)


@receiver(post_delete, sender=Advertisement)
def clear_deleted_ad_cache(sender, instance, **kwargs):
    """Clear cache when an ad is deleted."""
    if instance.slot:
        AdService.clear_ad_cache(slot_code=instance.slot.code)


@receiver(pre_save, sender=Advertisement)
def set_ad_defaults(sender, instance, **kwargs):
    """Set default values for ad before saving."""
    if not instance.pk:  # Only for new instances
        if not instance.priority:
            instance.priority = 0
        if not instance.is_active:
            instance.is_active = True
