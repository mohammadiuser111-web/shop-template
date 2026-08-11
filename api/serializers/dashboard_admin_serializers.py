"""
Serializers for dashboard_admin app.
"""
from rest_framework import serializers
from apps.dashboard_admin.models import (
    AdminDashboard,
    DashboardWidget,
    AdminMenu,
    AdminMenuItem,
    AdminQuickAction,
    AdminSettings,
    AdminUserSettings,
    AdminActivity,
)


class AdminDashboardSerializer(serializers.ModelSerializer):
    """Serializer for AdminDashboard model."""
    
    class Meta:
        model = AdminDashboard
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for DashboardWidget model."""
    
    class Meta:
        model = DashboardWidget
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class AdminMenuSerializer(serializers.ModelSerializer):
    """Serializer for AdminMenu model."""
    
    class Meta:
        model = AdminMenu
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class AdminMenuItemSerializer(serializers.ModelSerializer):
    """Serializer for AdminMenuItem model."""
    
    menu_name = serializers.CharField(source='menu.name', read_only=True)
    parent_title = serializers.CharField(source='parent.title', read_only=True, allow_null=True)
    
    class Meta:
        model = AdminMenuItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'menu_name', 'parent_title')


class AdminQuickActionSerializer(serializers.ModelSerializer):
    """Serializer for AdminQuickAction model."""
    
    class Meta:
        model = AdminQuickAction
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class AdminSettingsSerializer(serializers.ModelSerializer):
    """Serializer for AdminSettings model."""
    
    default_dashboard_name = serializers.CharField(source='default_dashboard.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AdminSettings
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'default_dashboard_name')


class AdminUserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for AdminUserSettings model."""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AdminUserSettings
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user_username', 'user_email', 'dashboard_name')


class AdminActivitySerializer(serializers.ModelSerializer):
    """Serializer for AdminActivity model."""
    
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    
    class Meta:
        model = AdminActivity
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'user_username', 'user_email')
