"""
Shipping API Views
ViewSets and APIViews for shipping models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.shipping.models import (
    ShippingMethod, ShippingZone, ShippingClass, 
    PickupLocation, DeliveryTime, ShippingRate
)
from api.serializers.shipping_serializers import (
    ShippingZoneSerializer,
    ShippingClassSerializer,
    PickupLocationSerializer,
    DeliveryTimeSerializer,
    ShippingRateSerializer,
    ShippingMethodSerializer,
    ShippingMethodListSerializer,
    ShippingMethodCreateSerializer,
    ShippingMethodUpdateSerializer,
    ShippingRateCreateSerializer,
    ShippingCalculatorSerializer,
    ShippingCostResultSerializer,
)
from api.pagination import CustomPageNumberPagination


class ShippingMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for ShippingMethod model"""
    
    serializer_class = ShippingMethodSerializer
    queryset = ShippingMethod.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ShippingMethodListSerializer
        elif self.action == 'create':
            return ShippingMethodCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ShippingMethodUpdateSerializer
        return ShippingMethodSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def zones(self, request, pk=None):
        shipping_method = self.get_object()
        zones = shipping_method.zones.all()
        serializer = ShippingZoneSerializer(zones, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def rates(self, request, pk=None):
        shipping_method = self.get_object()
        rates = ShippingRate.objects.filter(shipping_method=shipping_method)
        serializer = ShippingRateSerializer(rates, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def pickup_locations(self, request, pk=None):
        shipping_method = self.get_object()
        locations = shipping_method.pickup_locations.all()
        serializer = PickupLocationSerializer(locations, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def delivery_times(self, request, pk=None):
        shipping_method = self.get_object()
        times = shipping_method.delivery_times.all()
        serializer = DeliveryTimeSerializer(times, many=True, context={'request': request})
        return Response(serializer.data)


class ShippingZoneViewSet(viewsets.ModelViewSet):
    """ViewSet for ShippingZone model"""
    
    serializer_class = ShippingZoneSerializer
    queryset = ShippingZone.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def countries(self, request, pk=None):
        zone = self.get_object()
        serializer = self.get_serializer(zone, context={'request': request})
        return Response({'countries': serializer.data.get('countries', [])})


class ShippingClassViewSet(viewsets.ModelViewSet):
    """ViewSet for ShippingClass model"""
    
    serializer_class = ShippingClassSerializer
    queryset = ShippingClass.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class PickupLocationViewSet(viewsets.ModelViewSet):
    """ViewSet for PickupLocation model"""
    
    serializer_class = PickupLocationSerializer
    queryset = PickupLocation.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'address_line_1', 'city', 'state']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class DeliveryTimeViewSet(viewsets.ModelViewSet):
    """ViewSet for DeliveryTime model"""
    
    serializer_class = DeliveryTimeSerializer
    queryset = DeliveryTime.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'position', 'min_days', 'max_days']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class ShippingRateViewSet(viewsets.ModelViewSet):
    """ViewSet for ShippingRate model"""
    
    serializer_class = ShippingRateSerializer
    queryset = ShippingRate.objects.all().order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['shipping_method', 'shipping_zone', 'shipping_class']
    search_fields = ['name']
    ordering_fields = ['position', 'base_price']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class ShippingCalculatorAPIView(APIView):
    """APIView for shipping cost calculation"""
    
    permission_classes = [AllowAny]
    serializer_class = ShippingCalculatorSerializer
    
    def post(self, request):
        serializer = ShippingCalculatorSerializer(data=request.data)
        if serializer.is_valid():
            shipping_method_id = serializer.validated_data['shipping_method_id']
            shipping_zone_id = serializer.validated_data.get('shipping_zone_id')
            destination_country = serializer.validated_data.get('destination_country')
            destination_zip = serializer.validated_data.get('destination_zip')
            total_weight = serializer.validated_data['total_weight']
            item_count = serializer.validated_data['item_count']
            order_total = serializer.validated_data['order_total']
            
            # Get shipping method
            try:
                shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
            except ShippingMethod.DoesNotExist:
                return Response({'error': 'Shipping method not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Calculate shipping cost
            cost = shipping_method.calculate_cost(
                zone_id=shipping_zone_id,
                country=destination_country,
                zip_code=destination_zip,
                weight=total_weight,
                item_count=item_count,
                order_total=order_total
            )
            
            # Get estimated delivery
            estimated_delivery = shipping_method.get_estimated_delivery()
            
            # Get pickup locations
            pickup_locations = []
            for location in shipping_method.pickup_locations.filter(is_active=True):
                pickup_locations.append({
                    'id': location.id,
                    'name': location.name,
                    'address': location.get_full_address(),
                    'phone': location.phone,
                    'opening_hours': location.opening_hours
                })
            
            result = {
                'shipping_method': {
                    'id': shipping_method.id,
                    'name': shipping_method.name,
                    'code': shipping_method.code,
                    'description': shipping_method.description
                },
                'available_methods': [{
                    'id': sm.id,
                    'name': sm.name,
                    'code': sm.code
                } for sm in ShippingMethod.objects.filter(is_active=True)],
                'total_cost': float(cost),
                'estimated_delivery': estimated_delivery,
                'pickup_locations': pickup_locations
            }
            
            serializer = ShippingCostResultSerializer(result)
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ShippingStatsAPIView(APIView):
    """APIView for shipping statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count
        
        stats = {
            'total_shipping_methods': ShippingMethod.objects.count(),
            'active_shipping_methods': ShippingMethod.objects.filter(is_active=True).count(),
            'total_zones': ShippingZone.objects.count(),
            'active_zones': ShippingZone.objects.filter(is_active=True).count(),
            'total_locations': PickupLocation.objects.count(),
            'active_locations': PickupLocation.objects.filter(is_active=True).count(),
            'shipping_methods': [],
            'zones': [],
            'locations': []
        }
        
        # Shipping methods
        for method in ShippingMethod.objects.filter(is_active=True):
            stats['shipping_methods'].append({
                'id': method.id,
                'name': method.name,
                'code': method.code,
                'zone_count': method.zones.count(),
                'rate_count': method.rates.count(),
                'location_count': method.pickup_locations.count()
            })
        
        # Zones
        for zone in ShippingZone.objects.filter(is_active=True):
            stats['zones'].append({
                'id': zone.id,
                'name': zone.name,
                'code': zone.code,
                'country_count': zone.countries.count()
            })
        
        # Locations
        for location in PickupLocation.objects.filter(is_active=True):
            stats['locations'].append({
                'id': location.id,
                'name': location.name,
                'address': location.get_full_address(),
                'phone': location.phone
            })
        
        return Response(stats)
