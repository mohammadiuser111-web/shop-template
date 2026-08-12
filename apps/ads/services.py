"""
Services for ads app.
Handles ad display logic, rotation, and tracking.
"""
from django.utils import timezone
from django.core.cache import cache
from .models import AdSlot, Advertisement, AdImpression, AdClick
import random
import uuid


class AdService:
    """Main service for managing advertisements."""
    
    # Cache keys
    AD_SLOT_CACHE_KEY = 'ad_slot_{}'
    AD_CACHE_KEY = 'ad_{}'
    AD_IMPRESSION_CACHE_KEY = 'ad_impression_{}'
    AD_CLICK_CACHE_KEY = 'ad_click_{}'
    
    @classmethod
    def get_ad_slot(cls, slot_code):
        """Get ad slot by code with caching."""
        cache_key = cls.AD_SLOT_CACHE_KEY.format(slot_code)
        slot = cache.get(cache_key)
        
        if not slot:
            slot = AdSlot.objects.filter(code=slot_code, is_active=True).first()
            if slot:
                cache.set(cache_key, slot, timeout=3600)  # Cache for 1 hour
        
        return slot
    
    @classmethod
    def get_current_ad(cls, slot_code, request=None):
        """Get the current advertisement for a slot."""
        slot = cls.get_ad_slot(slot_code)
        
        if not slot:
            return None
        
        # Check cache first
        cache_key = cls.AD_CACHE_KEY.format(slot_code)
        ad_data = cache.get(cache_key)
        
        if ad_data:
            return ad_data.get('ad')
        
        # Get valid ads for this slot
        now = timezone.now()
        valid_ads = Advertisement.objects.filter(
            slot=slot,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).select_related('slot').order_by('-priority', '-created_at')
        
        if not valid_ads.exists():
            # Try without date constraints
            valid_ads = Advertisement.objects.filter(
                slot=slot,
                is_active=True
            ).select_related('slot').order_by('-priority', '-created_at')
        
        if valid_ads.exists():
            # Use round-robin for multiple ads with same priority
            ad = cls._get_round_robin_ad(slot_code, valid_ads)
            
            # Cache the result
            cache.set(cache_key, {'ad': ad, 'slot': slot}, timeout=300)  # Cache for 5 minutes
            return ad
        
        return None
    
    @classmethod
    def _get_round_robin_ad(cls, slot_code, ads):
        """Get ad using round-robin algorithm."""
        # Group ads by priority
        priority_groups = {}
        for ad in ads:
            priority = ad.priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(ad)
        
        # Get highest priority group
        max_priority = max(priority_groups.keys())
        highest_priority_ads = priority_groups[max_priority]
        
        # If only one ad at highest priority, return it
        if len(highest_priority_ads) == 1:
            return highest_priority_ads[0]
        
        # Use round-robin for multiple ads at same priority
        cache_key = f'ad_round_robin_{slot_code}_{max_priority}'
        last_index = cache.get(cache_key, 0)
        next_index = (last_index + 1) % len(highest_priority_ads)
        
        cache.set(cache_key, next_index, timeout=3600)
        
        return highest_priority_ads[next_index]
    
    @classmethod
    def track_impression(cls, ad, request=None, **kwargs):
        """Track an ad impression."""
        if not ad:
            return
        
        # Check if already tracked for this session
        session_key = f'ad_impression_{ad.id}'
        if request and hasattr(request, 'session') and request.session.get(session_key):
            return
        
        # Create impression record
        impression = AdImpression.objects.create(
            ad=ad,
            user=request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None,
            ip_address=cls._get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] if request else '',
            referrer=request.META.get('HTTP_REFERER', '') if request else '',
            **kwargs
        )
        
        # Update ad counter
        ad.increment_impressions()
        
        # Mark in session to prevent duplicate tracking
        if request and hasattr(request, 'session'):
            request.session[session_key] = True
        
        return impression
    
    @classmethod
    def track_click(cls, ad, request=None, **kwargs):
        """Track an ad click."""
        if not ad:
            return
        
        # Get the last impression for this user/session
        last_impression = None
        if request:
            last_impression = AdImpression.objects.filter(
                ad=ad,
                ip_address=cls._get_client_ip(request)
            ).order_by('-created_at').first()
        
        # Create click record
        click = AdClick.objects.create(
            ad=ad,
            impression=last_impression,
            user=request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None,
            ip_address=cls._get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] if request else '',
            referrer=request.META.get('HTTP_REFERER', '') if request else '',
            **kwargs
        )
        
        # Update ad counter
        ad.increment_clicks()
        
        return click
    
    @classmethod
    def get_ad_stats(cls, ad_id):
        """Get statistics for an ad."""
        ad = Advertisement.objects.filter(pk=ad_id).first()
        
        if not ad:
            return None
        
        # Get impressions and clicks
        impressions = AdImpression.objects.filter(ad=ad).count()
        clicks = AdClick.objects.filter(ad=ad).count()
        ctr = ad.get_ctr()
        
        return {
            'ad': ad,
            'impressions': impressions,
            'clicks': clicks,
            'ctr': ctr,
            'conversion_rate': 0,  # Would need conversion tracking
        }
    
    @classmethod
    def get_slot_stats(cls, slot_code):
        """Get statistics for an ad slot."""
        slot = cls.get_ad_slot(slot_code)
        
        if not slot:
            return None
        
        # Get all ads in this slot
        ads = Advertisement.objects.filter(slot=slot)
        
        total_impressions = sum(ad.impression_count for ad in ads)
        total_clicks = sum(ad.click_count for ad in ads)
        total_ads = ads.count()
        active_ads = ads.filter(is_active=True).count()
        
        return {
            'slot': slot,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_ads': total_ads,
            'active_ads': active_ads,
            'average_ctr': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
        }
    
    @classmethod
    def get_all_stats(cls):
        """Get overall advertisement statistics."""
        total_ads = Advertisement.objects.count()
        active_ads = Advertisement.objects.filter(is_active=True).count()
        total_impressions = AdImpression.objects.count()
        total_clicks = AdClick.objects.count()
        
        # Get top performing ads
        top_ads = Advertisement.objects.filter(click_count__gt=0).order_by('-click_count')[:5]
        
        return {
            'total_ads': total_ads,
            'active_ads': active_ads,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'overall_ctr': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
            'top_ads': top_ads,
        }
    
    @classmethod
    def _get_client_ip(cls, request):
        """Get client IP address."""
        if request is None:
            return None
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @classmethod
    def clear_ad_cache(cls, slot_code=None, ad_id=None):
        """Clear ad cache."""
        if slot_code:
            cache.delete(cls.AD_SLOT_CACHE_KEY.format(slot_code))
            cache.delete(cls.AD_CACHE_KEY.format(slot_code))
        
        if ad_id:
            cache.delete(cls.AD_CACHE_KEY.format(ad_id))
        
        # Clear round-robin cache
        cache.delete_pattern('ad_round_robin_*')


class AdRotationService:
    """Service for rotating ads."""
    
    @classmethod
    def get_rotating_ads(cls, slot_code, limit=5):
        """Get ads for rotation in a slot."""
        slot = AdService.get_ad_slot(slot_code)
        
        if not slot:
            return []
        
        now = timezone.now()
        ads = Advertisement.objects.filter(
            slot=slot,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).select_related('slot').order_by('-priority', '-created_at')[:limit]
        
        return list(ads)
    
    @classmethod
    def get_random_ad(cls, slot_code):
        """Get a random ad for a slot."""
        ads = cls.get_rotating_ads(slot_code)
        
        if ads:
            return random.choice(ads)
        return None


class AdTargetingService:
    """Service for targeted advertising."""
    
    @classmethod
    def get_targeted_ad(cls, slot_code, user=None, request=None):
        """Get an ad targeted to a specific user or criteria."""
        slot = AdService.get_ad_slot(slot_code)
        
        if not slot:
            return None
        
        now = timezone.now()
        
        # Get all valid ads for this slot
        valid_ads = Advertisement.objects.filter(
            slot=slot,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).select_related('slot').order_by('-priority')
        
        if not valid_ads.exists():
            return None
        
        # Apply targeting filters
        targeted_ads = []
        for ad in valid_ads:
            if cls._matches_targeting(ad, user, request):
                targeted_ads.append(ad)
        
        # If no targeted ads, return highest priority ad
        if not targeted_ads:
            return valid_ads.first()
        
        # Return the highest priority targeted ad
        return targeted_ads[0]
    
    @classmethod
    def _matches_targeting(cls, ad, user, request):
        """Check if ad matches targeting criteria."""
        # This would be extended with actual targeting logic
        # For now, always return True
        return True


class AdReportService:
    """Service for generating ad reports."""
    
    @classmethod
    def get_impression_report(cls, date_from=None, date_to=None, slot=None):
        """Get impression report."""
        queryset = AdImpression.objects.all()
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        if slot:
            queryset = queryset.filter(ad__slot=slot)
        
        # Group by date
        from django.db.models import Count, DateField
        from django.db.models.functions import TruncDate
        
        report = queryset.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return list(report)
    
    @classmethod
    def get_click_report(cls, date_from=None, date_to=None, slot=None):
        """Get click report."""
        queryset = AdClick.objects.all()
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        if slot:
            queryset = queryset.filter(ad__slot=slot)
        
        # Group by date
        from django.db.models import Count, DateField
        from django.db.models.functions import TruncDate
        
        report = queryset.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return list(report)
    
    @classmethod
    def get_performance_report(cls, date_from=None, date_to=None):
        """Get performance report for all ads."""
        from django.db.models import Sum
        
        queryset = Advertisement.objects.all()
        
        if date_from or date_to:
            # Filter by impression/click dates
            from django.db.models import Q
            queryset = queryset.filter(
                Q(impressions__created_at__gte=date_from) | Q(clicks__created_at__gte=date_from)
            )
            if date_to:
                queryset = queryset.filter(
                    Q(impressions__created_at__lte=date_to) | Q(clicks__created_at__lte=date_to)
                )
        
        report = queryset.annotate(
            total_impressions=Sum('impressions__id'),
            total_clicks=Sum('clicks__id')
        ).values(
            'id', 'name', 'slot__name', 'total_impressions', 'total_clicks'
        )
        
        # Calculate CTR
        for item in report:
            impressions = item['total_impressions'] or 0
            clicks = item['total_clicks'] or 0
            item['ctr'] = (clicks / impressions * 100) if impressions > 0 else 0
        
        return list(report)
