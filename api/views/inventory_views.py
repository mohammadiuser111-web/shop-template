"""
Inventory API Views
ViewSets and APIViews for inventory models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.inventory.models import (
    Supplier, InventoryLocation, StockMovement, PurchaseOrder, Inventory
)
from api.serializers.inventory_serializers import (
    SupplierSerializer,
    SupplierListSerializer,
    InventoryLocationSerializer,
    InventoryLocationListSerializer,
    StockMovementSerializer,
    StockMovementListSerializer,
    PurchaseOrderSerializer,
    PurchaseOrderListSerializer,
    InventorySerializer,
    InventoryListSerializer,
    InventoryUpdateSerializer,
    StockAdjustmentSerializer,
    InventoryTransferSerializer,
    InventoryStatsSerializer,
)
from api.pagination import CustomPageNumberPagination


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for Supplier model"""
    
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'email', 'phone', 'address']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SupplierListSerializer
        return SupplierSerializer
    
    def get_permissions(self):
        return [IsAdminUser()]


class InventoryLocationViewSet(viewsets.ModelViewSet):
    """ViewSet for InventoryLocation model"""
    
    serializer_class = InventoryLocationSerializer
    queryset = InventoryLocation.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'address_line_1', 'city', 'state']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InventoryLocationListSerializer
        return InventoryLocationSerializer
    
    def get_permissions(self):
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        location = self.get_object()
        inventory = Inventory.objects.filter(location=location)
        serializer = InventoryListSerializer(inventory, many=True, context={'request': request})
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ModelViewSet):
    """ViewSet for StockMovement model"""
    
    serializer_class = StockMovementSerializer
    queryset = StockMovement.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'product_variant', 'movement_type', 'user']
    search_fields = ['reference', 'notes']
    ordering_fields = ['created_at', 'quantity']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StockMovementListSerializer
        return StockMovementSerializer
    
    def get_permissions(self):
        return [IsAdminUser()]


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for PurchaseOrder model"""
    
    serializer_class = PurchaseOrderSerializer
    queryset = PurchaseOrder.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['supplier', 'status']
    search_fields = ['po_number', 'notes']
    ordering_fields = ['created_at', 'updated_at', 'total_cost']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer
    
    def get_permissions(self):
        return [IsAdminUser()]
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        purchase_order = self.get_object()
        
        if purchase_order.status != 'pending':
            return Response({'error': 'Purchase order cannot be received in current status'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update inventory
        for item in purchase_order.items.all():
            # TODO: Update inventory for each item
            pass
        
        # Update status
        purchase_order.status = 'received'
        purchase_order.save()
        
        return Response({'status': 'success', 'id': purchase_order.id})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        purchase_order = self.get_object()
        
        if purchase_order.status not in ['pending', 'processing']:
            return Response({'error': 'Purchase order cannot be cancelled in current status'}, status=status.HTTP_400_BAD_REQUEST)
        
        purchase_order.status = 'cancelled'
        purchase_order.save()
        
        return Response({'status': 'success', 'id': purchase_order.id})


class InventoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Inventory model"""
    
    serializer_class = InventorySerializer
    queryset = Inventory.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'product_variant', 'location', 'supplier']
    search_fields = ['product__name', 'product_variant__name', 'location__name']
    ordering_fields = ['quantity', 'reserved', 'last_updated']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InventoryListSerializer
        return InventorySerializer
    
    def get_permissions(self):
        return [IsAdminUser()]


class InventoryUpdateAPIView(APIView):
    """APIView for updating inventory"""
    
    permission_classes = [IsAdminUser]
    serializer_class = InventoryUpdateSerializer
    
    def post(self, request, pk):
        try:
            inventory = Inventory.objects.get(pk=pk)
        except Inventory.DoesNotExist:
            return Response({'error': 'Inventory not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = InventoryUpdateSerializer(inventory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class StockAdjustmentAPIView(APIView):
    """APIView for stock adjustments"""
    
    permission_classes = [IsAdminUser]
    serializer_class = StockAdjustmentSerializer
    
    def post(self, request):
        serializer = StockAdjustmentSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            variant_id = serializer.validated_data.get('variant_id')
            location_id = serializer.validated_data['location_id']
            adjustment = serializer.validated_data['adjustment']
            reason = serializer.validated_data['reason']
            reference = serializer.validated_data.get('reference', '')
            
            # Get product
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get variant if provided
            variant = None
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product)
                except ProductVariant.DoesNotExist:
                    return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get location
            try:
                location = InventoryLocation.objects.get(id=location_id)
            except InventoryLocation.DoesNotExist:
                return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get or create inventory
            inventory, created = Inventory.objects.get_or_create(
                product=product,
                product_variant=variant,
                location=location,
                defaults={'quantity': 0, 'reserved': 0}
            )
            
            # Adjust quantity
            old_quantity = inventory.quantity
            inventory.quantity += adjustment
            inventory.save()
            
            # Create stock movement
            StockMovement.objects.create(
                product=product,
                product_variant=variant,
                location=location,
                quantity=adjustment,
                movement_type='adjustment' if adjustment > 0 else 'deduction',
                reference=reference,
                notes=reason,
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'inventory_id': inventory.id,
                'old_quantity': old_quantity,
                'new_quantity': inventory.quantity
            })
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class InventoryTransferAPIView(APIView):
    """APIView for inventory transfers between locations"""
    
    permission_classes = [IsAdminUser]
    serializer_class = InventoryTransferSerializer
    
    def post(self, request):
        serializer = InventoryTransferSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            variant_id = serializer.validated_data.get('variant_id')
            from_location_id = serializer.validated_data['from_location_id']
            to_location_id = serializer.validated_data['to_location_id']
            quantity = serializer.validated_data['quantity']
            reason = serializer.validated_data['reason']
            
            # Get product
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get variant if provided
            variant = None
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product)
                except ProductVariant.DoesNotExist:
                    return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get locations
            try:
                from_location = InventoryLocation.objects.get(id=from_location_id)
                to_location = InventoryLocation.objects.get(id=to_location_id)
            except InventoryLocation.DoesNotExist:
                return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get inventory from source location
            try:
                from_inventory = Inventory.objects.get(
                    product=product,
                    product_variant=variant,
                    location=from_location
                )
            except Inventory.DoesNotExist:
                return Response({'error': 'Inventory not found at source location'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if enough stock
            if from_inventory.quantity < quantity:
                return Response({'error': 'Not enough stock at source location'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Deduct from source
            from_inventory.quantity -= quantity
            from_inventory.save()
            
            # Add to destination
            to_inventory, created = Inventory.objects.get_or_create(
                product=product,
                product_variant=variant,
                location=to_location,
                defaults={'quantity': 0, 'reserved': 0}
            )
            to_inventory.quantity += quantity
            to_inventory.save()
            
            # Create stock movements
            StockMovement.objects.create(
                product=product,
                product_variant=variant,
                location=from_location,
                quantity=-quantity,
                movement_type='transfer_out',
                reference=f'TR-{from_location.code}-{to_location.code}',
                notes=f'Transferred to {to_location.name}: {reason}',
                user=request.user
            )
            
            StockMovement.objects.create(
                product=product,
                product_variant=variant,
                location=to_location,
                quantity=quantity,
                movement_type='transfer_in',
                reference=f'TR-{from_location.code}-{to_location.code}',
                notes=f'Transferred from {from_location.name}: {reason}',
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'from_inventory_id': from_inventory.id,
                'to_inventory_id': to_inventory.id,
                'quantity': quantity
            })
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class InventoryStatsAPIView(APIView):
    """APIView for inventory statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count, Sum
        
        stats = {
            'total_products': Inventory.objects.values('product').distinct().count(),
            'total_variants': Inventory.objects.exclude(product_variant__isnull=True).values('product_variant').distinct().count(),
            'total_quantity': sum(i.quantity for i in Inventory.objects.all()) or 0,
            'low_stock_items': Inventory.objects.filter(quantity__lte=5).count(),
            'out_of_stock_items': Inventory.objects.filter(quantity=0).count(),
            'total_locations': InventoryLocation.objects.count(),
            'total_suppliers': Supplier.objects.count(),
            'inventory_by_location': {},
            'inventory_by_category': {},
            'recent_movements': []
        }
        
        # Inventory by location
        location_stats = Inventory.objects.values('location__name').annotate(
            total_quantity=Sum('quantity')
        )
        for stat in location_stats:
            stats['inventory_by_location'][stat['location__name']] = stat['total_quantity'] or 0
        
        # Inventory by category
        category_stats = Inventory.objects.values('product__categories__name').annotate(
            total_quantity=Sum('quantity')
        )
        for stat in category_stats:
            if stat['product__categories__name']:
                category_name = stat['product__categories__name']
                stats['inventory_by_category'][category_name] = stat['total_quantity'] or 0
        
        # Recent movements
        recent_movements = StockMovement.objects.order_by('-created_at')[:10]
        for movement in recent_movements:
            stats['recent_movements'].append({
                'id': movement.id,
                'product_name': movement.product.name,
                'variant_name': movement.product_variant.name if movement.product_variant else None,
                'location_name': movement.location.name,
                'quantity': movement.quantity,
                'movement_type': movement.movement_type,
                'created_at': movement.created_at
            })
        
        serializer = InventoryStatsSerializer(stats)
        return Response(serializer.data)
