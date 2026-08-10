"""
Core API Views
ViewSets and APIViews for core models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.models import (
    SiteSettings, ThemeConfig, Contact, AdminNote, SystemLog, Country, Currency
)
from api.serializers.core_serializers import (
    SiteSettingsSerializer,
    ThemeConfigSerializer,
    ContactSerializer,
    ContactListSerializer,
    AdminNoteSerializer,
    AdminNoteListSerializer,
    SystemLogSerializer,
    SystemLogListSerializer,
    CountrySerializer,
    CountryListSerializer,
    CurrencySerializer,
    SiteStatsSerializer,
)
from api.pagination import CustomPageNumberPagination


class SiteSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for SiteSettings model"""
    
    serializer_class = SiteSettingsSerializer
    queryset = SiteSettings.objects.all()
    permission_classes = [IsAdminUser]
    
    def get_object(self):
        return SiteSettings.objects.first()
    
    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({})
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            instance = SiteSettings.objects.create()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ThemeConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for ThemeConfig model"""
    
    serializer_class = ThemeConfigSerializer
    queryset = ThemeConfig.objects.all()
    permission_classes = [IsAdminUser]
    
    def get_object(self):
        return ThemeConfig.objects.first()
    
    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({})


class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet for Contact model"""
    
    serializer_class = ContactSerializer
    queryset = Contact.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_read', 'is_resolved', 'name', 'email']
    search_fields = ['name', 'email', 'subject', 'message']
    ordering_fields = ['created_at', 'updated_at', 'is_read', 'is_resolved']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContactListSerializer
        return ContactSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        contact = self.get_object()
        contact.is_read = True
        contact.save()
        return Response({'status': 'read', 'id': contact.id})
    
    @action(detail=True, methods=['post'])
    def mark_as_resolved(self, request, pk=None):
        contact = self.get_object()
        contact.is_resolved = True
        contact.save()
        return Response({'status': 'resolved', 'id': contact.id})


class AdminNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for AdminNote model"""
    
    serializer_class = AdminNoteSerializer
    queryset = AdminNote.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['note_type', 'is_pinned']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'is_pinned']
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AdminNoteListSerializer
        return AdminNoteSerializer


class SystemLogViewSet(viewsets.ModelViewSet):
    """ViewSet for SystemLog model"""
    
    serializer_class = SystemLogSerializer
    queryset = SystemLog.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['level', 'module']
    search_fields = ['message', 'module', 'details']
    ordering_fields = ['created_at', 'updated_at', 'level']
    permission_classes = [IsAdminUser]
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SystemLogListSerializer
        return SystemLogSerializer
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        days = request.data.get('days', 30)
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        deleted_count, _ = SystemLog.objects.filter(created_at__lt=cutoff).delete()
        return Response({'status': 'success', 'deleted_count': deleted_count})


class CountryViewSet(viewsets.ModelViewSet):
    """ViewSet for Country model"""
    
    serializer_class = CountrySerializer
    queryset = Country.objects.filter(is_active=True).order_by('name')
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'phone_code']
    ordering_fields = ['name', 'code', 'position']
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CountryListSerializer
        return CountrySerializer


class CurrencyViewSet(viewsets.ModelViewSet):
    """ViewSet for Currency model"""
    
    serializer_class = CurrencySerializer
    queryset = Currency.objects.filter(is_active=True).order_by('position')
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'symbol']
    ordering_fields = ['name', 'code', 'position']
    permission_classes = [AllowAny]


class SiteStatsAPIView(APIView):
    """APIView for site statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from apps.orders.models import Order
        from apps.products.models import Product
        from apps.accounts.models import User
        from apps.core.models import SiteSettings
        
        site_settings = SiteSettings.objects.first()
        
        stats = {
            'site_name': site_settings.site_name if site_settings else 'Shop Template',
            'site_description': site_settings.site_description if site_settings else '',
            'total_products': Product.objects.filter(is_published=True).count(),
            'total_orders': Order.objects.count(),
            'total_customers': User.objects.filter(is_active=True).count(),
            'total_revenue': sum(
                float(order.total) 
                for order in Order.objects.filter(status='delivered')
            ) if Order.objects.filter(status='delivered').exists() else 0,
            'active_products': Product.objects.filter(is_published=True, is_active=True).count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'recent_activity': []
        }
        
        # Add recent orders
        recent_orders = Order.objects.filter(status__in=['pending', 'processing']).order_by('-created_at')[:5]
        for order in recent_orders:
            stats['recent_activity'].append({
                'type': 'order',
                'id': order.id,
                'number': order.order_number,
                'status': order.status,
                'total': float(order.total),
                'created_at': order.created_at
            })
        
        # Add recent products
        recent_products = Product.objects.filter(is_published=True).order_by('-created_at')[:5]
        for product in recent_products:
            stats['recent_activity'].append({
                'type': 'product',
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'created_at': product.created_at
            })
        
        # Sort by created_at
        stats['recent_activity'].sort(key=lambda x: x['created_at'], reverse=True)
        stats['recent_activity'] = stats['recent_activity'][:10]
        
        serializer = SiteStatsSerializer(stats)
        return Response(serializer.data)


class HealthCheckAPIView(APIView):
    """APIView for health check"""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': self.request.timestamp,
            'service': 'shop-template-api'
        })
