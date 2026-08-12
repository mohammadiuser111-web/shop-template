"""
Filters for ads API.
"""
import django_filters
from ..models import AdSlot, Advertisement, AdImpression, AdClick


class AdSlotFilter(django_filters.FilterSet):
    """Filter for AdSlot model."""
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    is_responsive = django_filters.BooleanFilter()
    
    class Meta:
        model = AdSlot
        fields = ['name', 'code', 'is_active', 'is_responsive']


class AdvertisementFilter(django_filters.FilterSet):
    """Filter for Advertisement model."""
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    title = django_filters.CharFilter(lookup_expr='icontains')
    ad_type = django_filters.ChoiceFilter(
        choices=Advertisement.AD_TYPE_CHOICES
    )
    slot = django_filters.ModelChoiceFilter(
        queryset=AdSlot.objects.filter(is_active=True)
    )
    slot_code = django_filters.CharFilter(
        field_name='slot__code',
        lookup_expr='icontains'
    )
    is_active = django_filters.BooleanFilter()
    priority = django_filters.NumberFilter()
    priority__gte = django_filters.NumberFilter(field_name='priority', lookup_expr='gte')
    priority__lte = django_filters.NumberFilter(field_name='priority', lookup_expr='lte')
    start_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    class Meta:
        model = Advertisement
        fields = [
            'name', 'title', 'ad_type', 'slot', 'slot_code',
            'is_active', 'priority', 'start_date', 'end_date'
        ]


class AdImpressionFilter(django_filters.FilterSet):
    """Filter for AdImpression model."""
    
    ad = django_filters.ModelChoiceFilter(queryset=Advertisement.objects.all())
    ad_id = django_filters.UUIDFilter(field_name='ad__id')
    user = django_filters.ModelChoiceFilter(queryset=None)  # Will be set dynamically
    ip_address = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = AdImpression
        fields = ['ad', 'ad_id', 'user', 'ip_address', 'created_at']


class AdClickFilter(django_filters.FilterSet):
    """Filter for AdClick model."""
    
    ad = django_filters.ModelChoiceFilter(queryset=Advertisement.objects.all())
    ad_id = django_filters.UUIDFilter(field_name='ad__id')
    user = django_filters.ModelChoiceFilter(queryset=None)  # Will be set dynamically
    ip_address = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = AdClick
        fields = ['ad', 'ad_id', 'user', 'ip_address', 'created_at']
