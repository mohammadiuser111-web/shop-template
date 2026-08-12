"""
URL configuration for Core API.
"""
from django.urls import path
from . import views

app_name = 'core_api'

urlpatterns = [
    # SiteSettings
    path('settings/', views.SiteSettingsListCreateAPIView.as_view(), name='settings_list_create'),
    path('settings/current/', views.SiteSettingsRetrieveUpdateAPIView.as_view(), name='settings_current'),
    
    # ThemeConfig
    path('themes/', views.ThemeConfigListCreateAPIView.as_view(), name='theme_list_create'),
    path('themes/<uuid:pk>/', views.ThemeConfigRetrieveUpdateDestroyAPIView.as_view(), name='theme_detail'),
    path('themes/<uuid:pk>/activate/', views.ThemeConfigActivateAPIView.as_view(), name='theme_activate'),
    path('themes/<uuid:pk>/preview/', views.ThemePreviewAPIView.as_view(), name='theme_preview'),
    
    # ContactMessage
    path('contacts/', views.ContactMessageListCreateAPIView.as_view(), name='contact_list_create'),
    path('contacts/<uuid:pk>/', views.ContactMessageRetrieveUpdateDestroyAPIView.as_view(), name='contact_detail'),
    path('contacts/<uuid:pk>/read/', views.ContactMessageMarkReadAPIView.as_view(), name='contact_mark_read'),
    path('contacts/<uuid:pk>/archive/', views.ContactMessageArchiveAPIView.as_view(), name='contact_archive'),
    
    # AdminNote
    path('notes/', views.AdminNoteListCreateAPIView.as_view(), name='note_list_create'),
    path('notes/<uuid:pk>/', views.AdminNoteRetrieveUpdateDestroyAPIView.as_view(), name='note_detail'),
    path('notes/<uuid:pk>/complete/', views.AdminNoteCompleteAPIView.as_view(), name='note_complete'),
    
    # SystemLog
    path('logs/', views.SystemLogListAPIView.as_view(), name='log_list'),
    
    # Health Check
    path('health/', views.SiteHealthAPIView.as_view(), name='health_check'),
    path('info/', views.SiteInfoAPIView.as_view(), name='site_info'),
]
