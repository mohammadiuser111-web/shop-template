"""
API serializers for Notifications app.
"""
from rest_framework import serializers
from ..models import (
    Notification, NotificationTemplate,
    EmailNotification, PushNotification, SMSNotification, DeviceToken
)


# Notification Serializers
class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'read_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification list."""
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'notification_type', 'title', 'message', 'url',
                 'is_read', 'is_archived', 'priority', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notification."""
    
    class Meta:
        model = Notification
        fields = ['user', 'notification_type', 'title', 'message', 'url', 
                 'related_object_type', 'related_object_id', 'priority']


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification."""
    
    class Meta:
        model = Notification
        fields = ['is_read', 'is_archived']


# Notification Template Serializers
class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate."""
    
    class Meta:
        model = NotificationTemplate
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class NotificationTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification template list."""
    
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'name', 'code', 'notification_type', 'title_template', 'is_active']
        read_only_fields = ['id', 'code']


class NotificationTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notification template."""
    
    class Meta:
        model = NotificationTemplate
        fields = ['name', 'code', 'notification_type', 'title_template', 
                 'message_template', 'url_template', 'related_model', 'is_active']


# Email Notification Serializers
class EmailNotificationSerializer(serializers.ModelSerializer):
    """Serializer for EmailNotification."""
    
    to_user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = EmailNotification
        fields = '__all__'
        read_only_fields = ['id', 'to_user', 'is_sent', 'send_attempts', 'sent_at']


class EmailNotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for email notification list."""
    
    to_user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = EmailNotification
        fields = ['id', 'email_type', 'to_email', 'to_user', 'subject', 
                 'is_sent', 'send_attempts', 'created_at', 'sent_at']
        read_only_fields = ['id', 'to_user', 'is_sent', 'send_attempts', 'created_at', 'sent_at']


class EmailNotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating email notification."""
    
    class Meta:
        model = EmailNotification
        fields = ['email_type', 'to_email', 'to_user', 'subject', 'body', 'body_html']


# Push Notification Serializers
class PushNotificationSerializer(serializers.ModelSerializer):
    """Serializer for PushNotification."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = PushNotification
        fields = '__all__'
        read_only_fields = ['id', 'user', 'is_sent', 'created_at', 'sent_at']


class PushNotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for push notification list."""
    
    class Meta:
        model = PushNotification
        fields = ['id', 'user', 'title', 'body', 'url', 'is_sent', 'created_at']
        read_only_fields = ['id', 'user', 'is_sent', 'created_at']


class PushNotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating push notification."""
    
    class Meta:
        model = PushNotification
        fields = ['user', 'title', 'body', 'data', 'url']


# SMS Notification Serializers
class SMSNotificationSerializer(serializers.ModelSerializer):
    """Serializer for SMSNotification."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = SMSNotification
        fields = '__all__'
        read_only_fields = ['id', 'user', 'is_sent', 'send_attempts', 'created_at', 'sent_at']


class SMSNotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for SMS notification list."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = SMSNotification
        fields = ['id', 'phone_number', 'user', 'message', 'is_sent', 'send_attempts', 'created_at']
        read_only_fields = ['id', 'user', 'is_sent', 'send_attempts', 'created_at']


class SMSNotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SMS notification."""
    
    class Meta:
        model = SMSNotification
        fields = ['phone_number', 'user', 'message']


# Device Token Serializers
class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer for DeviceToken."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = DeviceToken
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class DeviceTokenListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for device token list."""
    
    class Meta:
        model = DeviceToken
        fields = ['id', 'user', 'token', 'device_type', 'device_name', 'is_active']
        read_only_fields = ['id', 'user']


class DeviceTokenCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating device token."""
    
    class Meta:
        model = DeviceToken
        fields = ['token', 'device_type', 'device_name', 'is_active']


# Notification Statistics Serializer
class NotificationStatisticsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""
    
    total_notifications = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    archived_count = serializers.IntegerField()
    total_emails = serializers.IntegerField()
    sent_emails = serializers.IntegerField()
    total_push = serializers.IntegerField()
    sent_push = serializers.IntegerField()
    total_sms = serializers.IntegerField()
    sent_sms = serializers.IntegerField()
