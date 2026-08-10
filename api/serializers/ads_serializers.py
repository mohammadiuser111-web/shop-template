"""
Ads Serializers
Serializers for ads models: AdSpace, AdBanner, AdImpression, AdClick
"""

from rest_framework import serializers
from apps.ads.models import AdSpace, AdBanner, AdImpression, AdClick
from .accounts_serializers import UserPublicSerializer


class AdSpaceSerializer(serializers.ModelSerializer):
    """Serializer for AdSpace model"""
    
    class Meta:
        model = AdSpace
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'space_id', 'slug')


class AdSpaceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ad space lists"""
    
    class Meta:
        model = AdSpace
        fields = ['id', 'space_id', 'name', 'code', 'description', 'width', 'height', 'is_active', 'position']
        read_only_fields = fields


class AdBannerSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for AdBanner model"""
    
    ad_space = AdSpaceSerializer(read_only=True)
    ad_space_id = serializers.IntegerField(write_only=True, required=True)
    created_by = UserPublicSerializer(read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    impressions = serializers.SerializerMethodField(read_only=True)
    clicks = serializers.SerializerMethodField(read_only=True)
    ctr = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AdBanner
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'banner_id', 'ad_space', 'created_by', 'image_url', 'impressions', 'clicks', 'ctr')
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
    
    def get_impressions(self, obj):
        return AdImpression.objects.filter(banner=obj).count()
    
    def get_clicks(self, obj):
        return AdClick.objects.filter(banner=obj).count()
    
    def get_ctr(self, obj):
        impressions = AdImpression.objects.filter(banner=obj).count()
        clicks = AdClick.objects.filter(banner=obj).count()
        if impressions > 0:
            return (clicks / impressions) * 100
        return 0


class AdBannerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ad banner lists"""
    
    ad_space_name = serializers.CharField(source='ad_space.name', read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    impressions = serializers.SerializerMethodField(read_only=True)
    clicks = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AdBanner
        fields = ['id', 'banner_id', 'title', 'ad_space_name', 'image_url', 'url', 'impressions', 'clicks', 'status_display', 'is_active', 'starts_at', 'ends_at', 'created_at']
        read_only_fields = fields
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
    
    def get_impressions(self, obj):
        return AdImpression.objects.filter(banner=obj).count()
    
    def get_clicks(self, obj):
        return AdClick.objects.filter(banner=obj).count()


class AdBannerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ad banners"""
    
    ad_space_id = serializers.IntegerField(required=True)
    
    class Meta:
        model = AdBanner
        fields = ['title', 'ad_space_id', 'image', 'url', 'content', 'target_blank', 'is_active', 'starts_at', 'ends_at', 'priority', 'customer_groups', 'devices']


class AdBannerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ad banners"""
    
    ad_space_id = serializers.IntegerField(required=False)
    
    class Meta:
        model = AdBanner
        fields = ['title', 'ad_space_id', 'image', 'url', 'content', 'target_blank', 'is_active', 'starts_at', 'ends_at', 'priority', 'customer_groups', 'devices']


class AdImpressionSerializer(serializers.ModelSerializer):
    """Serializer for AdImpression model"""
    
    banner = AdBannerListSerializer(read_only=True)
    
    class Meta:
        model = AdImpression
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'banner')


class AdClickSerializer(serializers.ModelSerializer):
    """Serializer for AdClick model"""
    
    banner = AdBannerListSerializer(read_only=True)
    user = UserPublicSerializer(read_only=True, allow_null=True)
    
    class Meta:
        model = AdClick
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'banner', 'user')


class AdImpressionCreateSerializer(serializers.Serializer):
    """Serializer for recording ad impressions"""
    
    banner_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    session_key = serializers.CharField(required=False, allow_blank=True)
    referrer = serializers.CharField(required=False, allow_blank=True)
    user_agent = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.CharField(required=False, allow_blank=True)


class AdClickCreateSerializer(serializers.Serializer):
    """Serializer for recording ad clicks"""
    
    banner_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    session_key = serializers.CharField(required=False, allow_blank=True)
    referrer = serializers.CharField(required=False, allow_blank=True)
    user_agent = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.CharField(required=False, allow_blank=True)


class AdStatsSerializer(serializers.Serializer):
    """Serializer for ad statistics"""
    
    total_spaces = serializers.IntegerField()
    total_banners = serializers.IntegerField()
    active_banners = serializers.IntegerField()
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    overall_ctr = serializers.FloatField()
    impressions_by_space = serializers.DictField()
    clicks_by_space = serializers.DictField()
    ctr_by_space = serializers.DictField()
    impressions_by_date = serializers.DictField()
    clicks_by_date = serializers.DictField()
    top_banners = serializers.ListField(child=serializers.DictField())
