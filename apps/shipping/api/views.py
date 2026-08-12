"""
API views for Shipping app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from ..models import ShippingZone, ShippingZoneLocation, ShippingMethod, ShippingClass, PickupLocation
from apps.orders.models import Order
from .serializers import (
    ShippingZoneSerializer, ShippingZoneListSerializer,
    ShippingZoneLocationSerializer, ShippingZoneLocationCreateSerializer,
    ShippingMethodSerializer, ShippingMethodListSerializer,
    ShippingMethodCreateSerializer, ShippingMethodCostSerializer,
    ShippingMethodCostResponseSerializer, ShippingClassSerializer,
    ShippingClassListSerializer, PickupLocationSerializer,
    PickupLocationListSerializer, ShippingStatisticsSerializer
)


# Shipping Zone Views
class ShippingZoneListAPIView(generics.ListAPIView):
    """List shipping zones."""
    
    serializer_class = ShippingZoneListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get shipping zones."""
        return ShippingZone.objects.filter(is_active=True).order_by('sort_order', 'name')


class ShippingZoneRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve shipping zone."""
    
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShippingZone.objects.all()


class ShippingZoneCreateAPIView(generics.CreateAPIView):
    """Create shipping zone."""
    
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.IsAdminUser]


class ShippingZoneUpdateAPIView(generics.UpdateAPIView):
    """Update shipping zone."""
    
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ShippingZone.objects.all()


class ShippingZoneDestroyAPIView(generics.DestroyAPIView):
    """Delete shipping zone."""
    
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ShippingZone.objects.all()


# Shipping Zone Location Views
class ShippingZoneLocationListAPIView(generics.ListAPIView):
    """List shipping zone locations."""
    
    serializer_class = ShippingZoneLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get shipping zone locations."""
        zone_id = self.kwargs.get('zone_id')
        if zone_id:
            zone = get_object_or_404(ShippingZone, pk=zone_id)
            return ShippingZoneLocation.objects.filter(zone=zone)
        return ShippingZoneLocation.objects.all()


class ShippingZoneLocationCreateAPIView(generics.CreateAPIView):
    """Create shipping zone location."""
    
    serializer_class = ShippingZoneLocationCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class ShippingZoneLocationDestroyAPIView(generics.DestroyAPIView):
    """Delete shipping zone location."""
    
    serializer_class = ShippingZoneLocationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ShippingZoneLocation.objects.all()


# Shipping Method Views
class ShippingMethodListAPIView(generics.ListAPIView):
    """List shipping methods."""
    
    serializer_class = ShippingMethodListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get shipping methods."""
        zone_id = self.kwargs.get('zone_id')
        if zone_id:
            zone = get_object_or_404(ShippingZone, pk=zone_id)
            return ShippingMethod.objects.filter(zone=zone, is_active=True).order_by('sort_order', 'name')
        return ShippingMethod.objects.filter(is_active=True).order_by('zone__sort_order', 'sort_order', 'name')


class ShippingMethodRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve shipping method."""
    
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShippingMethod.objects.all()


class ShippingMethodCreateAPIView(generics.CreateAPIView):
    """Create shipping method."""
    
    serializer_class = ShippingMethodCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class ShippingMethodUpdateAPIView(generics.UpdateAPIView):
    """Update shipping method."""
    
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ShippingMethod.objects.all()


class ShippingMethodDestroyAPIView(generics.DestroyAPIView):
    """Delete shipping method."""
    
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ShippingMethod.objects.all()


class ShippingMethodCostAPIView(views.APIView):
    """Calculate shipping cost for an order or cart."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Calculate shipping costs for all available methods."""
        serializer = ShippingMethodCostSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all active shipping methods
        methods = ShippingMethod.objects.filter(is_active=True).select_related('zone')
        
        results = []
        for method in methods:
            # Check minimum and maximum order amount
            order_total = serializer.validated_data['order_total']
            
            if method.min_order_amount and order_total < method.min_order_amount:
                results.append({
                    'method_id': method.id,
                    'method_name': method.name,
                    'cost': None,
                    'estimated_delivery': method.get_estimated_delivery(),
                    'is_available': False,
                    'message': f'Minimum order amount: {method.min_order_amount}'
                })
                continue
            
            if method.max_order_amount and order_total > method.max_order_amount:
                results.append({
                    'method_id': method.id,
                    'method_name': method.name,
                    'cost': None,
                    'estimated_delivery': method.get_estimated_delivery(),
                    'is_available': False,
                    'message': f'Maximum order amount: {method.max_order_amount}'
                })
                continue
            
            # Calculate cost based on pricing type
            cost = 0
            if method.is_free:
                cost = 0
            elif method.pricing_type == 'fixed':
                cost = method.base_price
            elif method.pricing_type == 'percentage':
                cost = order_total * (method.percentage / 100)
            elif method.pricing_type == 'per_item':
                item_count = serializer.validated_data.get('item_count', 0)
                cost = method.price_per_item * item_count
            elif method.pricing_type == 'per_weight':
                total_weight = serializer.validated_data.get('total_weight', 0)
                cost = method.price_per_kg * total_weight
            
            results.append({
                'method_id': method.id,
                'method_name': method.name,
                'cost': cost,
                'estimated_delivery': method.get_estimated_delivery(),
                'is_available': True,
                'message': ''
            })
        
        return Response(results, status=status.HTTP_200_OK)


# Shipping Class Views
class ShippingClassListAPIView(generics.ListAPIView):
    """List shipping classes."""
    
    serializer_class = ShippingClassListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShippingClass.objects.all().order_by('name')


class ShippingClassRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve shipping class."""
    
    serializer_class = ShippingClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShippingClass.objects.all()


class ShippingClassCreateAPIView(generics.CreateAPIView):
    """Create shipping class."""
    
    serializer_class = ShippingClassSerializer
    permission_classes = [permissions.IsAdminUser]


class ShippingClassUpdateAPIView(generics.UpdateAPIView):
    """Update shipping class."""
    
    serializer_class = ShippingClassSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ShippingClass.objects.all()


class ShippingClassDestroyAPIView(generics.DestroyAPIView):
    """Delete shipping class."""
    
    serializer_class = ShippingClassSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ShippingClass.objects.all()


# Pickup Location Views
class PickupLocationListAPIView(generics.ListAPIView):
    """List pickup locations."""
    
    serializer_class = PickupLocationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get pickup locations."""
        return PickupLocation.objects.filter(is_active=True).order_by('sort_order', 'name')


class PickupLocationRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve pickup location."""
    
    serializer_class = PickupLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PickupLocation.objects.all()


class PickupLocationCreateAPIView(generics.CreateAPIView):
    """Create pickup location."""
    
    serializer_class = PickupLocationSerializer
    permission_classes = [permissions.IsAdminUser]


class PickupLocationUpdateAPIView(generics.UpdateAPIView):
    """Update pickup location."""
    
    serializer_class = PickupLocationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = PickupLocation.objects.all()


class PickupLocationDestroyAPIView(generics.DestroyAPIView):
    """Delete pickup location."""
    
    serializer_class = PickupLocationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = PickupLocation.objects.all()


# Shipping Statistics View
class ShippingStatisticsAPIView(views.APIView):
    """Get shipping statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Return shipping statistics."""
        from django.db.models import Count, Avg
        
        data = {
            'total_zones': ShippingZone.objects.count(),
            'total_methods': ShippingMethod.objects.count(),
            'total_pickup_locations': PickupLocation.objects.count(),
            'active_methods': ShippingMethod.objects.filter(is_active=True).count(),
            'average_shipping_cost': ShippingMethod.objects.aggregate(
                avg_cost=Avg('base_price')
            )['avg_cost'] or 0
        }
        
        serializer = ShippingStatisticsSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


# Available Shipping Methods View
class AvailableShippingMethodsAPIView(views.APIView):
    """Get available shipping methods for checkout."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return available shipping methods."""
        # Get all active shipping methods
        methods = ShippingMethod.objects.filter(is_active=True).select_related('zone').order_by('sort_order', 'name')
        
        serializer = ShippingMethodListSerializer(methods, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
