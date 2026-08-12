"""
Serializers for Core API.
"""
from rest_framework import serializers
from ..models import SiteSettings, ThemeConfig, ContactMessage, AdminNote, SystemLog


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SiteSettings model."""
    
    class Meta:
        model = SiteSettings
        fields = [
            'id', 'site_name', 'site_description', 'site_logo', 'site_favicon',
            'site_url', 'default_language', 'default_currency', 'default_timezone',
            'maintenance_mode', 'maintenance_message', 'google_analytics',
            'facebook_pixel', 'meta_tags', 'custom_css', 'custom_js',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ThemeConfigSerializer(serializers.ModelSerializer):
    """Serializer for ThemeConfig model."""
    
    class Meta:
        model = ThemeConfig
        fields = [
            'id', 'theme_name', 'primary_color', 'secondary_color', 'success_color',
            'danger_color', 'warning_color', 'info_color', 'light_color', 'dark_color',
            'background_color', 'text_color', 'font_family', 'font_size',
            'border_radius', 'shadow_size', 'is_dark_mode', 'rtl_support',
            'custom_css', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for ContactMessage model."""
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'message',
            'is_read', 'is_archived', 'response', 'responded_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_read', 'is_archived', 'responded_by', 'created_at', 'updated_at']


class AdminNoteSerializer(serializers.ModelSerializer):
    """Serializer for AdminNote model."""
    
    class Meta:
        model = AdminNote
        fields = [
            'id', 'title', 'content', 'note_type', 'priority',
            'created_by', 'assigned_to', 'is_completed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class SystemLogSerializer(serializers.ModelSerializer):
    """Serializer for SystemLog model."""
    
    class Meta:
        model = SystemLog
        fields = [
            'id', 'log_type', 'message', 'data', 'ip_address',
            'user_agent', 'user', 'created_at'
        ]
        read_only_fields = ['id', 'ip_address', 'user_agent', 'user', 'created_at']


class SiteHealthSerializer(serializers.Serializer):
    """Serializer for site health check."""
    
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    django_version = serializers.CharField()
    python_version = serializers.CharField()
    database_status = serializers.CharField()
    cache_status = serializers.CharField()
    storage_status = serializers.CharField()
    
    class Meta:
        fields = [
            'status', 'timestamp', 'django_version', 'python_version',
            'database_status', 'cache_status', 'storage_status'
        ]


class ThemePreviewSerializer(serializers.Serializer):
    """Serializer for theme preview."""
    
    theme_name = serializers.CharField()
    colors = serializers.DictField()
    fonts = serializers.DictField()
    preview_image = serializers.URLField(required=False, allow_null=True)
    
    class Meta:
        fields = ['theme_name', 'colors', 'fonts', 'preview_image']
