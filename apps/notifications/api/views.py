"""
API views for Notifications app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from ..models import (
    Notification, NotificationTemplate,
    EmailNotification, PushNotification, SMSNotification, DeviceToken
)
from .serializers import (
    NotificationSerializer, NotificationListSerializer,
    NotificationCreateSerializer, NotificationUpdateSerializer,
    NotificationTemplateSerializer, NotificationTemplateListSerializer,
    NotificationTemplateCreateSerializer, EmailNotificationSerializer,
    EmailNotificationListSerializer, EmailNotificationCreateSerializer,
    PushNotificationSerializer, PushNotificationListSerializer,
    PushNotificationCreateSerializer, SMSNotificationSerializer,
    SMSNotificationListSerializer, SMSNotificationCreateSerializer,
    DeviceTokenSerializer, DeviceTokenListSerializer,
    DeviceTokenCreateSerializer, NotificationStatisticsSerializer
)


# Notification Views
class NotificationListAPIView(generics.ListAPIView):
    """List notifications."""
    
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's notifications."""
        is_read = self.request.query_params.get('read')
        is_archived = self.request.query_params.get('archived')
        
        queryset = Notification.objects.filter(user=self.request.user)
        
        if is_read:
            if is_read == 'true':
                queryset = queryset.filter(is_read=True)
            elif is_read == 'false':
                queryset = queryset.filter(is_read=False)
        
        if is_archived:
            if is_archived == 'true':
                queryset = queryset.filter(is_archived=True)
            elif is_archived == 'false':
                queryset = queryset.filter(is_archived=False)
        
        return queryset.order_by('-priority', '-created_at')


class NotificationRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve notification."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's notifications."""
        return Notification.objects.filter(user=self.request.user)


class NotificationCreateAPIView(generics.CreateAPIView):
    """Create notification."""
    
    serializer_class = NotificationCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class NotificationUpdateAPIView(generics.UpdateAPIView):
    """Update notification."""
    
    serializer_class = NotificationUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's notifications."""
        return Notification.objects.filter(user=self.request.user)


class NotificationDestroyAPIView(generics.DestroyAPIView):
    """Delete notification."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's notifications."""
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkAsReadAPIView(views.APIView):
    """Mark notification as read."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Mark notification as read."""
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_as_read()
        
        serializer = NotificationSerializer(notification, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationMarkAllAsReadAPIView(views.APIView):
    """Mark all notifications as read."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Mark all notifications as read."""
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        count = notifications.count()
        notifications.update(is_read=True, read_at=timezone.now())
        
        return Response({
            'detail': f'{count} notifications marked as read'
        }, status=status.HTTP_200_OK)


class NotificationArchiveAPIView(views.APIView):
    """Archive notification."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Archive notification."""
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_as_archived()
        
        serializer = NotificationSerializer(notification, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Notification Template Views
class NotificationTemplateListAPIView(generics.ListAPIView):
    """List notification templates."""
    
    serializer_class = NotificationTemplateListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = NotificationTemplate.objects.filter(is_active=True).order_by('name')


class NotificationTemplateRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve notification template."""
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = NotificationTemplate.objects.all()


class NotificationTemplateCreateAPIView(generics.CreateAPIView):
    """Create notification template."""
    
    serializer_class = NotificationTemplateCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class NotificationTemplateUpdateAPIView(generics.UpdateAPIView):
    """Update notification template."""
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = NotificationTemplate.objects.all()


class NotificationTemplateDestroyAPIView(generics.DestroyAPIView):
    """Delete notification template."""
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = NotificationTemplate.objects.all()


# Email Notification Views
class EmailNotificationListAPIView(generics.ListAPIView):
    """List email notifications."""
    
    serializer_class = EmailNotificationListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = EmailNotification.objects.all().order_by('-created_at')


class EmailNotificationRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve email notification."""
    
    serializer_class = EmailNotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = EmailNotification.objects.all()


class EmailNotificationCreateAPIView(generics.CreateAPIView):
    """Create email notification."""
    
    serializer_class = EmailNotificationCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class EmailNotificationDestroyAPIView(generics.DestroyAPIView):
    """Delete email notification."""
    
    serializer_class = EmailNotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = EmailNotification.objects.all()


# Push Notification Views
class PushNotificationListAPIView(generics.ListAPIView):
    """List push notifications."""
    
    serializer_class = PushNotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's push notifications."""
        return PushNotification.objects.filter(user=self.request.user).order_by('-created_at')


class PushNotificationRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve push notification."""
    
    serializer_class = PushNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's push notifications."""
        return PushNotification.objects.filter(user=self.request.user)


class PushNotificationCreateAPIView(generics.CreateAPIView):
    """Create push notification."""
    
    serializer_class = PushNotificationCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class PushNotificationDestroyAPIView(generics.DestroyAPIView):
    """Delete push notification."""
    
    serializer_class = PushNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's push notifications."""
        return PushNotification.objects.filter(user=self.request.user)


# SMS Notification Views
class SMSNotificationListAPIView(generics.ListAPIView):
    """List SMS notifications."""
    
    serializer_class = SMSNotificationListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SMSNotification.objects.all().order_by('-created_at')


class SMSNotificationRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve SMS notification."""
    
    serializer_class = SMSNotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SMSNotification.objects.all()


class SMSNotificationCreateAPIView(generics.CreateAPIView):
    """Create SMS notification."""
    
    serializer_class = SMSNotificationCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class SMSNotificationDestroyAPIView(generics.DestroyAPIView):
    """Delete SMS notification."""
    
    serializer_class = SMSNotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SMSNotification.objects.all()


# Device Token Views
class DeviceTokenListAPIView(generics.ListAPIView):
    """List device tokens."""
    
    serializer_class = DeviceTokenListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's device tokens."""
        return DeviceToken.objects.filter(user=self.request.user, is_active=True)


class DeviceTokenRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve device token."""
    
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's device tokens."""
        return DeviceToken.objects.filter(user=self.request.user)


class DeviceTokenCreateAPIView(generics.CreateAPIView):
    """Create device token."""
    
    serializer_class = DeviceTokenCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set user."""
        serializer.save(user=self.request.user)


class DeviceTokenUpdateAPIView(generics.UpdateAPIView):
    """Update device token."""
    
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's device tokens."""
        return DeviceToken.objects.filter(user=self.request.user)


class DeviceTokenDestroyAPIView(generics.DestroyAPIView):
    """Delete device token."""
    
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's device tokens."""
        return DeviceToken.objects.filter(user=self.request.user)


# Notification Statistics View
class NotificationStatisticsAPIView(views.APIView):
    """Get notification statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Return notification statistics."""
        # Total notifications
        total_notifications = Notification.objects.count()
        
        # Unread count
        unread_count = Notification.objects.filter(is_read=False).count()
        
        # Archived count
        archived_count = Notification.objects.filter(is_archived=True).count()
        
        # Email notifications
        total_emails = EmailNotification.objects.count()
        sent_emails = EmailNotification.objects.filter(is_sent=True).count()
        
        # Push notifications
        total_push = PushNotification.objects.count()
        sent_push = PushNotification.objects.filter(is_sent=True).count()
        
        # SMS notifications
        total_sms = SMSNotification.objects.count()
        sent_sms = SMSNotification.objects.filter(is_sent=True).count()
        
        data = {
            'total_notifications': total_notifications,
            'unread_count': unread_count,
            'archived_count': archived_count,
            'total_emails': total_emails,
            'sent_emails': sent_emails,
            'total_push': total_push,
            'sent_push': sent_push,
            'total_sms': total_sms,
            'sent_sms': sent_sms
        }
        
        serializer = NotificationStatisticsSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


# Unread Notifications Count View
class UnreadNotificationsCountAPIView(views.APIView):
    """Get unread notifications count."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Return unread notifications count."""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return Response({'count': count}, status=status.HTTP_200_OK)
