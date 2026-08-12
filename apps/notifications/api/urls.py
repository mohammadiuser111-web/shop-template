"""
API URLs for Notifications app.
"""
from django.urls import path
from .views import (
    # Notification views
    NotificationListAPIView, NotificationRetrieveAPIView,
    NotificationCreateAPIView, NotificationUpdateAPIView,
    NotificationDestroyAPIView, NotificationMarkAsReadAPIView,
    NotificationMarkAllAsReadAPIView, NotificationArchiveAPIView,
    # Notification Template views
    NotificationTemplateListAPIView, NotificationTemplateRetrieveAPIView,
    NotificationTemplateCreateAPIView, NotificationTemplateUpdateAPIView,
    NotificationTemplateDestroyAPIView,
    # Email Notification views
    EmailNotificationListAPIView, EmailNotificationRetrieveAPIView,
    EmailNotificationCreateAPIView, EmailNotificationDestroyAPIView,
    # Push Notification views
    PushNotificationListAPIView, PushNotificationRetrieveAPIView,
    PushNotificationCreateAPIView, PushNotificationDestroyAPIView,
    # SMS Notification views
    SMSNotificationListAPIView, SMSNotificationRetrieveAPIView,
    SMSNotificationCreateAPIView, SMSNotificationDestroyAPIView,
    # Device Token views
    DeviceTokenListAPIView, DeviceTokenRetrieveAPIView,
    DeviceTokenCreateAPIView, DeviceTokenUpdateAPIView,
    DeviceTokenDestroyAPIView,
    # Statistics
    NotificationStatisticsAPIView, UnreadNotificationsCountAPIView
)

urlpatterns = [
    # Notifications
    path('notifications/', NotificationListAPIView.as_view(), name='api-notifications-list'),
    path('notifications/<uuid:pk>/', NotificationRetrieveAPIView.as_view(), name='api-notifications-retrieve'),
    path('notifications/create/', NotificationCreateAPIView.as_view(), name='api-notifications-create'),
    path('notifications/<uuid:pk>/update/', NotificationUpdateAPIView.as_view(), name='api-notifications-update'),
    path('notifications/<uuid:pk>/delete/', NotificationDestroyAPIView.as_view(), name='api-notifications-delete'),
    path('notifications/<uuid:pk>/read/', NotificationMarkAsReadAPIView.as_view(), name='api-notifications-read'),
    path('notifications/mark-all-read/', NotificationMarkAllAsReadAPIView.as_view(), name='api-notifications-mark-all-read'),
    path('notifications/<uuid:pk>/archive/', NotificationArchiveAPIView.as_view(), name='api-notifications-archive'),
    path('notifications/unread-count/', UnreadNotificationsCountAPIView.as_view(), name='api-notifications-unread-count'),
    
    # Notification Templates
    path('templates/', NotificationTemplateListAPIView.as_view(), name='api-notification-templates-list'),
    path('templates/<uuid:pk>/', NotificationTemplateRetrieveAPIView.as_view(), name='api-notification-templates-retrieve'),
    path('templates/create/', NotificationTemplateCreateAPIView.as_view(), name='api-notification-templates-create'),
    path('templates/<uuid:pk>/update/', NotificationTemplateUpdateAPIView.as_view(), name='api-notification-templates-update'),
    path('templates/<uuid:pk>/delete/', NotificationTemplateDestroyAPIView.as_view(), name='api-notification-templates-delete'),
    
    # Email Notifications
    path('emails/', EmailNotificationListAPIView.as_view(), name='api-email-notifications-list'),
    path('emails/<uuid:pk>/', EmailNotificationRetrieveAPIView.as_view(), name='api-email-notifications-retrieve'),
    path('emails/create/', EmailNotificationCreateAPIView.as_view(), name='api-email-notifications-create'),
    path('emails/<uuid:pk>/delete/', EmailNotificationDestroyAPIView.as_view(), name='api-email-notifications-delete'),
    
    # Push Notifications
    path('push/', PushNotificationListAPIView.as_view(), name='api-push-notifications-list'),
    path('push/<uuid:pk>/', PushNotificationRetrieveAPIView.as_view(), name='api-push-notifications-retrieve'),
    path('push/create/', PushNotificationCreateAPIView.as_view(), name='api-push-notifications-create'),
    path('push/<uuid:pk>/delete/', PushNotificationDestroyAPIView.as_view(), name='api-push-notifications-delete'),
    
    # SMS Notifications
    path('sms/', SMSNotificationListAPIView.as_view(), name='api-sms-notifications-list'),
    path('sms/<uuid:pk>/', SMSNotificationRetrieveAPIView.as_view(), name='api-sms-notifications-retrieve'),
    path('sms/create/', SMSNotificationCreateAPIView.as_view(), name='api-sms-notifications-create'),
    path('sms/<uuid:pk>/delete/', SMSNotificationDestroyAPIView.as_view(), name='api-sms-notifications-delete'),
    
    # Device Tokens
    path('devices/', DeviceTokenListAPIView.as_view(), name='api-device-tokens-list'),
    path('devices/<uuid:pk>/', DeviceTokenRetrieveAPIView.as_view(), name='api-device-tokens-retrieve'),
    path('devices/create/', DeviceTokenCreateAPIView.as_view(), name='api-device-tokens-create'),
    path('devices/<uuid:pk>/update/', DeviceTokenUpdateAPIView.as_view(), name='api-device-tokens-update'),
    path('devices/<uuid:pk>/delete/', DeviceTokenDestroyAPIView.as_view(), name='api-device-tokens-delete'),
    
    # Statistics
    path('statistics/', NotificationStatisticsAPIView.as_view(), name='api-notifications-statistics'),
]
