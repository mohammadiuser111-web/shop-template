"""
API Views for dashboard_admin app.
REST API endpoints for admin dashboard management.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

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

from api.serializers.dashboard_admin_serializers import (
    AdminDashboardSerializer,
    DashboardWidgetSerializer,
    AdminMenuSerializer,
    AdminMenuItemSerializer,
    AdminQuickActionSerializer,
    AdminSettingsSerializer,
    AdminUserSettingsSerializer,
    AdminActivitySerializer,
)

from api.pagination import CustomPageNumberPagination
from api.permissions import IsAdminOrReadOnly


class AdminDashboardViewSet(viewsets.ModelViewSet):
    """API endpoint for AdminDashboard model."""
    
    queryset = AdminDashboard.objects.filter(is_active=True)
    serializer_class = AdminDashboardSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_default', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at', 'sort_order']
    ordering = ['-is_default', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """Override to allow non-admin users to see their own dashboards."""
        if self.request.user.is_superuser:
            return AdminDashboard.objects.all()
        return AdminDashboard.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        """Set default values on creation."""
        if serializer.validated_data.get('is_default', False):
            # Ensure only one default dashboard
            AdminDashboard.objects.filter(is_default=True).update(is_default=False)
        serializer.save()
    
    def perform_update(self, serializer):
        """Handle default dashboard updates."""
        if serializer.validated_data.get('is_default', False):
            AdminDashboard.objects.filter(is_default=True).exclude(pk=self.get_object().pk).update(is_default=False)
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this dashboard as default."""
        dashboard = self.get_object()
        AdminDashboard.objects.filter(is_default=True).update(is_default=False)
        dashboard.is_default = True
        dashboard.save()
        return Response({'status': 'success', 'message': 'Dashboard set as default'})


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """API endpoint for DashboardWidget model."""
    
    queryset = DashboardWidget.objects.filter(is_active=True)
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['widget_type', 'is_active']
    search_fields = ['name', 'code', 'title']
    ordering_fields = ['name', 'code', 'sort_order', 'created_at']
    ordering = ['sort_order']
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """Override to allow filtering by dashboard."""
        queryset = super().get_queryset()
        dashboard_id = self.request.query_params.get('dashboard_id')
        if dashboard_id:
            # Filter widgets by dashboard configuration
            # This would need to be implemented based on how widgets are assigned to dashboards
            pass
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle widget active status."""
        widget = self.get_object()
        widget.is_active = not widget.is_active
        widget.save()
        return Response({
            'status': 'success',
            'is_active': widget.is_active
        })
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder widgets."""
        widget_ids = request.data.get('widget_ids', [])
        for index, widget_id in enumerate(widget_ids):
            try:
                widget = DashboardWidget.objects.get(id=widget_id)
                widget.sort_order = index
                widget.save()
            except DashboardWidget.DoesNotExist:
                pass
        return Response({'status': 'success'})


class AdminMenuViewSet(viewsets.ModelViewSet):
    """API endpoint for AdminMenu model."""
    
    queryset = AdminMenu.objects.filter(is_active=True)
    serializer_class = AdminMenuSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['menu_type', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'menu_type', 'sort_order', 'created_at']
    ordering = ['menu_type', 'sort_order']
    pagination_class = CustomPageNumberPagination


class AdminMenuItemViewSet(viewsets.ModelViewSet):
    """API endpoint for AdminMenuItem model."""
    
    queryset = AdminMenuItem.objects.filter(is_visible=True)
    serializer_class = AdminMenuItemSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['menu', 'parent', 'item_type', 'is_visible']
    search_fields = ['title', 'url']
    ordering_fields = ['menu', 'parent', 'sort_order', 'created_at']
    ordering = ['menu__sort_order', 'parent__sort_order', 'sort_order']
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """Override to filter by menu type."""
        queryset = super().get_queryset()
        menu_type = self.request.query_params.get('menu_type')
        if menu_type:
            queryset = queryset.filter(menu__menu_type=menu_type)
        return queryset


class AdminQuickActionViewSet(viewsets.ModelViewSet):
    """API endpoint for AdminQuickAction model."""
    
    queryset = AdminQuickAction.objects.filter(is_active=True)
    serializer_class = AdminQuickActionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action_type', 'is_active']
    search_fields = ['name', 'code', 'title']
    ordering_fields = ['name', 'code', 'sort_order', 'created_at']
    ordering = ['sort_order']
    pagination_class = CustomPageNumberPagination
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a quick action."""
        action = self.get_object()
        # Implement action execution logic based on action_type
        return Response({
            'status': 'success',
            'message': f'Action {action.name} executed'
        })


class AdminSettingsViewSet(viewsets.ModelViewSet):
    """API endpoint for AdminSettings model (Singleton)."""
    
    queryset = AdminSettings.objects.all()
    serializer_class = AdminSettingsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Return only the singleton instance."""
        return AdminSettings.objects.all()
    
    def list(self, request, *args, **kwargs):
        """Return the singleton instance."""
        instance = AdminSettings.get_instance()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response([])
    
    def create(self, request, *args, **kwargs):
        """Prevent creation of multiple instances."""
        if AdminSettings.objects.exists():
            return Response(
                {'error': 'Only one AdminSettings instance is allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        """Update the singleton instance."""
        instance = AdminSettings.get_instance()
        if instance:
            serializer.save()
        else:
            serializer.save(pk=1)


class AdminUserSettingsViewSet(viewsets.ModelViewSet):
    """API endpoint for AdminUserSettings model."""
    
    serializer_class = AdminUserSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's settings."""
        if self.request.user.is_superuser:
            return AdminUserSettings.objects.all()
        return AdminUserSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get the current user's settings."""
        obj = super().get_object()
        return obj
    
    def perform_create(self, serializer):
        """Set user to current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's settings."""
        settings, created = AdminUserSettings.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_me(self, request):
        """Update current user's settings."""
        settings, created = AdminUserSettings.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminActivityViewSet(viewsets.ModelViewSet):
    """API endpoint for AdminActivity model."""
    
    queryset = AdminActivity.objects.all()
    serializer_class = AdminActivitySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'model_name', 'user']
    search_fields = ['user__username', 'model_name', 'object_repr', 'description', 'ip_address']
    ordering_fields = ['created_at', 'action', 'model_name']
    ordering = ['-created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """Override to filter by current user unless superuser."""
        if self.request.user.is_superuser:
            return AdminActivity.objects.all()
        return AdminActivity.objects.filter(user=self.request.user)


class DashboardStatsAPIView(viewsets.ViewSet):
    """API endpoint for dashboard statistics."""
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """Return dashboard statistics."""
        from apps.products.models import Product
        from apps.orders.models import Order
        from apps.accounts.models import User
        from apps.payments.models import Payment
        from django.db.models import Count, Sum
        from django.utils import timezone
        
        today = timezone.now().date()
        
        stats = {
            'products': {
                'total': Product.objects.count(),
                'active': Product.objects.filter(is_active=True).count(),
                'out_of_stock': Product.objects.filter(inventory__quantity__lte=0).count(),
            },
            'orders': {
                'total': Order.objects.count(),
                'pending': Order.objects.filter(status='pending').count(),
                'completed': Order.objects.filter(status='completed').count(),
                'today': Order.objects.filter(created_at__date=today).count(),
                'total_revenue': float(Order.objects.filter(status='completed').aggregate(
                    total=Sum('total_amount')
                )['total'] or 0),
            },
            'users': {
                'total': User.objects.count(),
                'active': User.objects.filter(is_active=True).count(),
                'staff': User.objects.filter(is_staff=True).count(),
                'today': User.objects.filter(date_joined__date=today).count(),
            },
            'payments': {
                'total': Payment.objects.count(),
                'successful': Payment.objects.filter(status='completed').count(),
                'today': Payment.objects.filter(created_at__date=today).count(),
            },
        }
        
        return Response(stats)


class AdminSettingsAPIView(viewsets.ViewSet):
    """API endpoint for admin settings management."""
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get admin settings."""
        settings = AdminSettings.get_instance()
        if settings:
            serializer = AdminSettingsSerializer(settings)
            return Response(serializer.data)
        return Response({})
    
    def post(self, request):
        """Update admin settings."""
        settings = AdminSettings.get_instance()
        if not settings:
            settings = AdminSettings()
        
        serializer = AdminSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
