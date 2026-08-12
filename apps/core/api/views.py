"""
API views for Core app.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils import timezone
import django
import sys
import platform

from ..models import SiteSettings, ThemeConfig, ContactMessage, AdminNote, SystemLog
from .serializers import (
    SiteSettingsSerializer, ThemeConfigSerializer,
    ContactMessageSerializer, AdminNoteSerializer,
    SystemLogSerializer, SiteHealthSerializer, ThemePreviewSerializer
)


# SiteSettings Views
class SiteSettingsListCreateAPIView(generics.ListCreateAPIView):
    """List and create site settings."""
    
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Return only one settings instance."""
        return SiteSettings.objects.order_by('-created_at')[:1]
    
    def perform_create(self, serializer):
        """Ensure only one settings instance exists."""
        # Delete existing settings if any
        SiteSettings.objects.all().delete()
        serializer.save()


class SiteSettingsRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve and update site settings."""
    
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self):
        """Get or create settings instance."""
        obj = SiteSettings.objects.order_by('-created_at').first()
        if not obj:
            obj = SiteSettings.objects.create()
        return obj


# ThemeConfig Views
class ThemeConfigListCreateAPIView(generics.ListCreateAPIView):
    """List and create theme configurations."""
    
    queryset = ThemeConfig.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ThemeConfigSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter by active status."""
        is_active = self.request.query_params.get('is_active')
        if is_active:
            return ThemeConfig.objects.filter(is_active=(is_active.lower() == 'true'))
        return ThemeConfig.objects.all().order_by('-created_at')


class ThemeConfigRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete theme configuration."""
    
    queryset = ThemeConfig.objects.all()
    serializer_class = ThemeConfigSerializer
    permission_classes = [permissions.IsAdminUser]


class ThemeConfigActivateAPIView(APIView):
    """Activate a theme configuration."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        """Activate theme by ID."""
        theme = generics.get_object_or_404(ThemeConfig, pk=pk)
        
        # Deactivate all other themes
        ThemeConfig.objects.update(is_active=False)
        
        # Activate selected theme
        theme.is_active = True
        theme.save()
        
        serializer = ThemeConfigSerializer(theme)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ThemePreviewAPIView(APIView):
    """Preview a theme configuration."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        """Get theme preview."""
        theme = generics.get_object_or_404(ThemeConfig, pk=pk)
        
        data = {
            'theme_name': theme.theme_name,
            'colors': {
                'primary': theme.primary_color,
                'secondary': theme.secondary_color,
                'success': theme.success_color,
                'danger': theme.danger_color,
                'warning': theme.warning_color,
                'info': theme.info_color,
                'light': theme.light_color,
                'dark': theme.dark_color,
                'background': theme.background_color,
                'text': theme.text_color,
            },
            'fonts': {
                'family': theme.font_family,
                'size': theme.font_size,
            },
            'preview_image': None,  # Would need to generate or have predefined
        }
        
        serializer = ThemePreviewSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ContactMessage Views
class ContactMessageListCreateAPIView(generics.ListCreateAPIView):
    """List and create contact messages."""
    
    queryset = ContactMessage.objects.filter(is_archived=False).order_by('-created_at')
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter by read/archived status."""
        queryset = super().get_queryset()
        
        is_read = self.request.query_params.get('is_read')
        if is_read:
            queryset = queryset.filter(is_read=(is_read.lower() == 'true'))
        
        is_archived = self.request.query_params.get('is_archived')
        if is_archived:
            queryset = queryset.filter(is_archived=(is_archived.lower() == 'true'))
        
        return queryset
    
    def perform_create(self, serializer):
        """Create contact message."""
        serializer.save()


class ContactMessageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete contact message."""
    
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]


class ContactMessageMarkReadAPIView(APIView):
    """Mark contact message as read."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        """Mark message as read."""
        message = generics.get_object_or_404(ContactMessage, pk=pk)
        message.is_read = True
        message.save()
        
        serializer = ContactMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContactMessageArchiveAPIView(APIView):
    """Archive contact message."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        """Archive message."""
        message = generics.get_object_or_404(ContactMessage, pk=pk)
        message.is_archived = True
        message.save()
        
        serializer = ContactMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)


# AdminNote Views
class AdminNoteListCreateAPIView(generics.ListCreateAPIView):
    """List and create admin notes."""
    
    serializer_class = AdminNoteSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter notes."""
        queryset = AdminNote.objects.filter(created_by=self.request.user)
        
        note_type = self.request.query_params.get('note_type')
        if note_type:
            queryset = queryset.filter(note_type=note_type)
        
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        is_completed = self.request.query_params.get('is_completed')
        if is_completed:
            queryset = queryset.filter(is_completed=(is_completed.lower() == 'true'))
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create note."""
        serializer.save(created_by=self.request.user)


class AdminNoteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete admin note."""
    
    queryset = AdminNote.objects.all()
    serializer_class = AdminNoteSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter by user."""
        if self.request.user.is_superuser:
            return AdminNote.objects.all()
        return AdminNote.objects.filter(created_by=self.request.user)


class AdminNoteCompleteAPIView(APIView):
    """Mark admin note as completed."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        """Mark note as completed."""
        note = generics.get_object_or_404(AdminNote, pk=pk)
        note.is_completed = True
        note.save()
        
        serializer = AdminNoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)


# SystemLog Views
class SystemLogListAPIView(generics.ListAPIView):
    """List system logs."""
    
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter logs."""
        queryset = SystemLog.objects.all()
        
        log_type = self.request.query_params.get('log_type')
        if log_type:
            queryset = queryset.filter(log_type=log_type)
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')[:100]  # Limit to 100 logs


# Health Check Views
class SiteHealthAPIView(APIView):
    """Check site health status."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return site health status."""
        from django.db import connection
        from django.core.cache import cache
        from django.conf import settings
        import os
        
        # Check database
        db_status = "healthy"
        try:
            connection.cursor()
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Check cache
        cache_status = "healthy"
        try:
            cache.set('health_check', 'test', 10)
            cache.get('health_check')
        except Exception as e:
            cache_status = f"error: {str(e)}"
        
        # Check storage
        storage_status = "healthy"
        try:
            test_path = os.path.join(settings.MEDIA_ROOT, 'health_check.txt')
            with open(test_path, 'w') as f:
                f.write('test')
            os.remove(test_path)
        except Exception as e:
            storage_status = f"error: {str(e)}"
        
        data = {
            'status': 'healthy' if db_status == 'healthy' and cache_status == 'healthy' else 'degraded',
            'timestamp': timezone.now(),
            'django_version': django.get_version(),
            'python_version': platform.python_version(),
            'database_status': db_status,
            'cache_status': cache_status,
            'storage_status': storage_status,
        }
        
        serializer = SiteHealthSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SiteInfoAPIView(APIView):
    """Get site information."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return site information."""
        settings = SiteSettings.objects.order_by('-created_at').first()
        
        if settings:
            serializer = SiteSettingsSerializer(settings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({
            'site_name': 'Shop Template',
            'site_description': 'Professional E-commerce Template',
        }, status=status.HTTP_200_OK)
