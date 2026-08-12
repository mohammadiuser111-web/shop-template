"""
Serializers for ads API.
"""
from rest_framework import serializers
from ..models import AdSlot, Advertisement, AdImpression, AdClick


class AdSlotSerializer(serializers.ModelSerializer):
    """Serializer for AdSlot model."""
    
    class Meta:
        model = AdSlot
        fields = [
            'id', 'name', 'code', 'description', 
            'width', 'height', 'is_responsive', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer for Advertisement model."""
    
    slot = AdSlotSerializer(read_only=True)
    slot_id = serializers.UUIDField(write_only=True, required=True)
    
    class Meta:
        model = Advertisement
        fields = [
            'id', 'name', 'slot', 'slot_id', 'ad_type',
            'image', 'image_alt', 'html_content', 'script_content',
            'video_url', 'video_embed_code', 'url', 'target',
            'title', 'description', 'priority', 'start_date', 'end_date',
            'is_active', 'created_by', 'created_at', 'updated_at',
            'impression_count', 'click_count'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 
            'impression_count', 'click_count', 'slot'
        ]


class AdImpressionSerializer(serializers.ModelSerializer):
    """Serializer for AdImpression model."""
    
    ad = AdvertisementSerializer(read_only=True)
    ad_id = serializers.UUIDField(write_only=True, required=True)
    
    class Meta:
        model = AdImpression
        fields = [
            'id', 'ad', 'ad_id', 'user', 'ip_address',
            'user_agent', 'referrer', 'session_key', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'ad']


class AdClickSerializer(serializers.ModelSerializer):
    """Serializer for AdClick model."""
    
    ad = AdvertisementSerializer(read_only=True)
    ad_id = serializers.UUIDField(write_only=True, required=True)
    impression = AdImpressionSerializer(read_only=True)
    impression_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = AdClick
        fields = [
            'id', 'ad', 'ad_id', 'impression', 'impression_id',
            'user', 'ip_address', 'user_agent', 'referrer',
            'session_key', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'ad', 'impression']


class AdvertisementStatsSerializer(serializers.Serializer):
    """Serializer for advertisement statistics."""
    
    id = serializers.UUIDField()
    name = serializers.CharField()
    title = serializers.CharField()
    ad_type = serializers.CharField()
    impression_count = serializers.IntegerField()
    click_count = serializers.IntegerField()
    ctr = serializers.FloatField()
    
    class Meta:
        fields = ['id', 'name', 'title', 'ad_type', 'impression_count', 'click_count', 'ctr']


class AdSlotStatsSerializer(serializers.Serializer):
    """Serializer for ad slot statistics."""
    
    id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    total_ads = serializers.IntegerField()
    active_ads = serializers.IntegerField()
    average_ctr = serializers.FloatField()
    
    class Meta:
        fields = ['id', 'name', 'code', 'total_impressions', 'total_clicks', 'total_ads', 'active_ads', 'average_ctr']


class AdsOverallStatsSerializer(serializers.Serializer):
    """Serializer for overall ads statistics."""
    
    total_ads = serializers.IntegerField()
    active_ads = serializers.IntegerField()
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    overall_ctr = serializers.FloatField()
    top_ads = AdvertisementStatsSerializer(many=True)
    
    class Meta:
        fields = ['total_ads', 'active_ads', 'total_impressions', 'total_clicks', 'overall_ctr', 'top_ads']


class AdDisplaySerializer(serializers.Serializer):
    """Serializer for ad display."""
    
    id = serializers.UUIDField()
    name = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    ad_type = serializers.CharField()
    image_url = serializers.URLField(required=False, allow_null=True)
    html_content = serializers.CharField(required=False, allow_null=True)
    script_content = serializers.CharField(required=False, allow_null=True)
    video_url = serializers.URLField(required=False, allow_null=True)
    video_embed_code = serializers.CharField(required=False, allow_null=True)
    url = serializers.URLField(required=False, allow_null=True)
    target = serializers.CharField()
    priority = serializers.IntegerField()
    is_active = serializers.BooleanField()
    
    class Meta:
        fields = [
            'id', 'name', 'title', 'description', 'ad_type',
            'image_url', 'html_content', 'script_content',
            'video_url', 'video_embed_code', 'url', 'target',
            'priority', 'is_active'
        ]


class ReportDataSerializer(serializers.Serializer):
    """Serializer for report data."""
    
    date = serializers.DateField()
    count = serializers.IntegerField()
    
    class Meta:
        fields = ['date', 'count']


class PerformanceReportSerializer(serializers.Serializer):
    """Serializer for performance report."""
    
    ad_id = serializers.CharField()
    name = serializers.CharField()
    slot_name = serializers.CharField()
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    ctr = serializers.FloatField()
    
    class Meta:
        fields = ['ad_id', 'name', 'slot_name', 'total_impressions', 'total_clicks', 'ctr']
