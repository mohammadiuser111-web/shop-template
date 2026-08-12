"""
API views for Inventory app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import uuid

from ..models import Warehouse, Inventory, InventoryMovement, StockAlert, Supplier, PurchaseOrder, PurchaseOrderItem
from apps.products.models import Product, ProductVariant
from .serializers import (
    WarehouseSerializer, WarehouseListSerializer,
    InventorySerializer, InventoryListSerializer,
    InventoryCreateSerializer, InventoryUpdateSerializer,
    InventoryStockUpdateSerializer, InventoryMovementSerializer,
    InventoryMovementListSerializer, StockAlertSerializer,
    StockAlertListSerializer, SupplierSerializer,
    SupplierListSerializer, PurchaseOrderSerializer,
    PurchaseOrderListSerializer, PurchaseOrderCreateSerializer,
    PurchaseOrderItemCreateSerializer, InventoryStatisticsSerializer
)


# Warehouse Views
class WarehouseListAPIView(generics.ListAPIView):
    """List warehouses."""
    
    serializer_class = WarehouseListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get warehouses."""
        return Warehouse.objects.filter(is_active=True).order_by('sort_order', 'name')


class WarehouseRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve warehouse."""
    
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Warehouse.objects.all()


class WarehouseCreateAPIView(generics.CreateAPIView):
    """Create warehouse."""
    
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAdminUser]


class WarehouseUpdateAPIView(generics.UpdateAPIView):
    """Update warehouse."""
    
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Warehouse.objects.all()


class WarehouseDestroyAPIView(generics.DestroyAPIView):
    """Delete warehouse."""
    
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Warehouse.objects.all()


# Inventory Views
class InventoryListAPIView(generics.ListAPIView):
    """List inventory records."""
    
    serializer_class = InventoryListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get inventory records."""
        warehouse_id = self.kwargs.get('warehouse_id')
        product_id = self.kwargs.get('product_id')
        
        queryset = Inventory.objects.filter(is_active=True)
        
        if warehouse_id:
            warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
            queryset = queryset.filter(warehouse=warehouse)
        
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            queryset = queryset.filter(product=product)
        
        return queryset.select_related('product', 'variant', 'warehouse').order_by('-updated_at')


class InventoryRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve inventory record."""
    
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Inventory.objects.all()


class InventoryCreateAPIView(generics.CreateAPIView):
    """Create inventory record."""
    
    serializer_class = InventoryCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class InventoryUpdateAPIView(generics.UpdateAPIView):
    """Update inventory record."""
    
    serializer_class = InventoryUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Inventory.objects.all()


class InventoryStockUpdateAPIView(views.APIView):
    """Update inventory stock."""
    
    permission_classes = [permissions.IsAdminUser]
    
    @transaction.atomic
    def post(self, request):
        """Update inventory stock."""
        serializer = InventoryStockUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = serializer.validated_data['product_id']
        variant_id = serializer.validated_data.get('variant_id')
        warehouse_id = serializer.validated_data['warehouse_id']
        quantity_change = serializer.validated_data['quantity_change']
        reason = serializer.validated_data.get('reason', '')
        
        # Get inventory record
        inventory = get_object_or_404(Inventory, product_id=product_id, variant_id=variant_id, warehouse_id=warehouse_id)
        
        # Update quantity
        old_quantity = inventory.quantity
        new_quantity = old_quantity + quantity_change
        
        if new_quantity < 0:
            return Response({'detail': 'Quantity cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)
        
        inventory.quantity = new_quantity
        inventory.save()
        
        # Create movement record
        movement_type = 'in' if quantity_change > 0 else 'out'
        InventoryMovement.objects.create(
            inventory=inventory,
            movement_type=movement_type,
            quantity=quantity_change,
            quantity_after=new_quantity,
            reference_type='manual_adjustment',
            reference_id=None,
            user=request.user,
            notes=reason
        )
        
        serializer = InventorySerializer(inventory, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class InventoryBulkUpdateAPIView(views.APIView):
    """Bulk update inventory."""
    
    permission_classes = [permissions.IsAdminUser]
    
    @transaction.atomic
    def post(self, request):
        """Bulk update inventory."""
        updates = request.data.get('updates', [])
        
        if not updates:
            return Response({'detail': 'No updates provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        for update_data in updates:
            product_id = update_data.get('product_id')
            variant_id = update_data.get('variant_id')
            warehouse_id = update_data.get('warehouse_id')
            quantity = update_data.get('quantity')
            
            if not product_id or not warehouse_id or quantity is None:
                results.append({'status': 'error', 'message': 'Missing required fields'})
                continue
            
            try:
                inventory, created = Inventory.objects.get_or_create(
                    product_id=product_id,
                    variant_id=variant_id,
                    warehouse_id=warehouse_id,
                    defaults={'quantity': 0}
                )
                
                old_quantity = inventory.quantity
                inventory.quantity = quantity
                inventory.save()
                
                # Create movement record
                InventoryMovement.objects.create(
                    inventory=inventory,
                    movement_type='adjustment',
                    quantity=quantity - old_quantity,
                    quantity_after=quantity,
                    reference_type='bulk_update',
                    reference_id=None,
                    user=request.user,
                    notes='Bulk inventory update'
                )
                
                results.append({'status': 'success', 'inventory_id': inventory.id})
            except Exception as e:
                results.append({'status': 'error', 'message': str(e)})
        
        return Response({'results': results}, status=status.HTTP_200_OK)


# Inventory Movement Views
class InventoryMovementListAPIView(generics.ListAPIView):
    """List inventory movements."""
    
    serializer_class = InventoryMovementListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get inventory movements."""
        inventory_id = self.kwargs.get('inventory_id')
        
        if inventory_id:
            inventory = get_object_or_404(Inventory, pk=inventory_id)
            return InventoryMovement.objects.filter(inventory=inventory)
        
        return InventoryMovement.objects.all()


class InventoryMovementRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve inventory movement."""
    
    serializer_class = InventoryMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = InventoryMovement.objects.all()


# Stock Alert Views
class StockAlertListAPIView(generics.ListAPIView):
    """List stock alerts."""
    
    serializer_class = StockAlertListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get stock alerts."""
        warehouse_id = self.kwargs.get('warehouse_id')
        
        queryset = StockAlert.objects.all()
        
        if warehouse_id:
            warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
            queryset = queryset.filter(warehouse=warehouse)
        
        return queryset.order_by('-created_at')


class StockAlertRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve stock alert."""
    
    serializer_class = StockAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = StockAlert.objects.all()


# Supplier Views
class SupplierListAPIView(generics.ListAPIView):
    """List suppliers."""
    
    serializer_class = SupplierListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get suppliers."""
        return Supplier.objects.filter(is_active=True).order_by('name')


class SupplierRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve supplier."""
    
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Supplier.objects.all()


class SupplierCreateAPIView(generics.CreateAPIView):
    """Create supplier."""
    
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAdminUser]


class SupplierUpdateAPIView(generics.UpdateAPIView):
    """Update supplier."""
    
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Supplier.objects.all()


class SupplierDestroyAPIView(generics.DestroyAPIView):
    """Delete supplier."""
    
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Supplier.objects.all()


# Purchase Order Views
class PurchaseOrderListAPIView(generics.ListAPIView):
    """List purchase orders."""
    
    serializer_class = PurchaseOrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get purchase orders."""
        supplier_id = self.kwargs.get('supplier_id')
        warehouse_id = self.kwargs.get('warehouse_id')
        status = self.request.query_params.get('status')
        
        queryset = PurchaseOrder.objects.all()
        
        if supplier_id:
            supplier = get_object_or_404(Supplier, pk=supplier_id)
            queryset = queryset.filter(supplier=supplier)
        
        if warehouse_id:
            warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
            queryset = queryset.filter(warehouse=warehouse)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('supplier', 'warehouse').order_by('-created_at')


class PurchaseOrderRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve purchase order."""
    
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PurchaseOrder.objects.all()


class PurchaseOrderCreateAPIView(generics.CreateAPIView):
    """Create purchase order."""
    
    serializer_class = PurchaseOrderCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        """Create purchase order."""
        # Generate PO number
        po_number = f"PO-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        
        serializer.save(
            po_number=po_number,
            created_by=self.request.user,
            order_date=timezone.now().date()
        )


class PurchaseOrderUpdateAPIView(generics.UpdateAPIView):
    """Update purchase order."""
    
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = PurchaseOrder.objects.all()


class PurchaseOrderItemListAPIView(generics.ListAPIView):
    """List purchase order items."""
    
    serializer_class = serializers.Serializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get purchase order items."""
        po_id = self.kwargs.get('po_id')
        po = get_object_or_404(PurchaseOrder, pk=po_id)
        return PurchaseOrderItem.objects.filter(purchase_order=po)


class PurchaseOrderItemCreateAPIView(generics.CreateAPIView):
    """Create purchase order item."""
    
    serializer_class = PurchaseOrderItemCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        """Create purchase order item."""
        po_id = self.kwargs.get('po_id')
        po = get_object_or_404(PurchaseOrder, pk=po_id)
        serializer.save(purchase_order=po)
        
        # Recalculate PO totals
        po.calculate_totals()


# Inventory Statistics View
class InventoryStatisticsAPIView(views.APIView):
    """Get inventory statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Return inventory statistics."""
        from django.db.models import Count, Sum
        
        # Total warehouses
        total_warehouses = Warehouse.objects.count()
        
        # Total products with inventory
        products_with_inventory = Inventory.objects.values('product').distinct().count()
        
        # Total suppliers
        total_suppliers = Supplier.objects.count()
        
        # Total purchase orders
        total_purchase_orders = PurchaseOrder.objects.count()
        
        # Low stock count
        low_stock_count = Inventory.objects.filter(is_active=True).exclude(
            models.Q(quantity__gte=models.F('low_stock_threshold'))
        ).count()
        
        # Out of stock count
        out_of_stock_count = Inventory.objects.filter(is_active=True, quantity=0).count()
        
        # Total inventory value (using average price from products)
        from apps.products.models import Product
        inventory_value = sum(
            inv.quantity * inv.product.price 
            for inv in Inventory.objects.filter(is_active=True).select_related('product')
        )
        
        data = {
            'total_warehouses': total_warehouses,
            'total_products': products_with_inventory,
            'total_suppliers': total_suppliers,
            'total_purchase_orders': total_purchase_orders,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_inventory_value': inventory_value
        }
        
        serializer = InventoryStatisticsSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


# Product Inventory View
class ProductInventoryAPIView(views.APIView):
    """Get inventory for a product across all warehouses."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, product_id):
        """Return inventory for a product."""
        product = get_object_or_404(Product, pk=product_id)
        
        # Get inventory records for this product
        inventory_records = Inventory.objects.filter(
            product=product,
            is_active=True
        ).select_related('warehouse', 'variant')
        
        # Group by warehouse and variant
        data = []
        for record in inventory_records:
            data.append({
                'warehouse_id': record.warehouse.id,
                'warehouse_name': record.warehouse.name,
                'variant_id': record.variant.id if record.variant else None,
                'variant_name': record.variant.name if record.variant else 'N/A',
                'quantity': record.quantity,
                'reserved_quantity': record.reserved_quantity,
                'available_quantity': record.get_available_quantity(),
                'location': record.location,
                'is_low_stock': record.is_low_stock(),
                'is_out_of_stock': record.is_out_of_stock()
            })
        
        return Response(data, status=status.HTTP_200_OK)
