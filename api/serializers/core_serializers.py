"""
Core Serializers
Serializers for core models: SiteSettings, ThemeConfig, Contact, AdminNote, SystemLog
"""

from rest_framework import serializers
from apps.core.models import SiteSettings, ThemeConfig, Contact, AdminNote, SystemLog, Country, Currency


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for Country model"""
    
    flag_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Country
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'code', 'flag_url')
    
    def get_flag_url(self, obj):
        if obj.flag:
            return self.context['request'].build_absolute_uri(obj.flag.url)
        return None


class CountryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for country lists"""
    
    class Meta:
        model = Country
        fields = ['id', 'code', 'name', 'is_active', 'phone_code']
        read_only_fields = fields


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for Currency model"""
    
    class Meta:
        model = Currency
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'code')


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SiteSettings model"""
    
    logo_url = serializers.SerializerMethodField(read_only=True)
    favicon_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SiteSettings
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'logo_url', 'favicon_url')
    
    def get_logo_url(self, obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None
    
    def get_favicon_url(self, obj):
        if obj.favicon:
            return self.context['request'].build_absolute_uri(obj.favicon.url)
        return None


class ThemeConfigSerializer(serializers.ModelSerializer):
    """Serializer for ThemeConfig model"""
    
    class Meta:
        model = ThemeConfig
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for Contact model"""
    
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'ticket_id')


class ContactListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for contact lists"""
    
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'subject', 'is_read', 'is_resolved', 'created_at']
        read_only_fields = fields


class AdminNoteSerializer(serializers.ModelSerializer):
    """Serializer for AdminNote model"""
    
    class Meta:
        model = AdminNote
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class AdminNoteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for admin note lists"""
    
    class Meta:
        model = AdminNote
        fields = ['id', 'title', 'note_type', 'is_pinned', 'created_at']
        read_only_fields = fields


class SystemLogSerializer(serializers.ModelSerializer):
    """Serializer for SystemLog model"""
    
    class Meta:
        model = SystemLog
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class SystemLogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for system log lists"""
    
    class Meta:
        model = SystemLog
        fields = ['id', 'level', 'message', 'module', 'created_at']
        read_only_fields = fields


class SiteStatsSerializer(serializers.Serializer):
    """Serializer for site statistics"""
    
    site_name = serializers.CharField()
    site_description = serializers.CharField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    active_products = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    recent_activity = serializers.ListField(child=serializers.DictField())


class ThemeSerializer(serializers.Serializer):
    """Serializer for theme configuration"""
    
    name = serializers.CharField()
    display_name = serializers.CharField()
    version = serializers.CharField()
    author = serializers.CharField()
    description = serializers.CharField()
    screenshot = serializers.CharField()
    is_active = serializers.BooleanField()
    settings = serializers.DictField()
