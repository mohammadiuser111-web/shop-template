"""
Inventory Serializers
Serializers for inventory models: Inventory, InventoryLocation, Supplier, PurchaseOrder, StockMovement
"""

from rest_framework import serializers
from apps.inventory.models import (
    Inventory, InventoryLocation, Supplier, PurchaseOrder, StockMovement
)
from apps.products.models import Product, ProductVariant
from .products_serializers import ProductListSerializer, ProductVariantSerializer
from .accounts_serializers import UserPublicSerializer


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model"""
    
    contact_person = UserPublicSerializer(read_only=True)
    contact_person_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug', 'supplier_id')


class SupplierListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for supplier lists"""
    
    class Meta:
        model = Supplier
        fields = ['id', 'supplier_id', 'name', 'email', 'phone', 'address', 'is_active', 'created_at']
        read_only_fields = fields


class InventoryLocationSerializer(serializers.ModelSerializer):
    """Serializer for InventoryLocation model"""
    
    class Meta:
        model = InventoryLocation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'location_id')


class InventoryLocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for inventory location lists"""
    
    class Meta:
        model = InventoryLocation
        fields = ['id', 'location_id', 'name', 'address', 'is_active', 'created_at']
        read_only_fields = fields


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model"""
    
    user = UserPublicSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    product_variant = ProductVariantSerializer(read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user', 'product', 'product_variant', 'movement_type_display')


class StockMovementListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for stock movement lists"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='product_variant.name', read_only=True, allow_null=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = ['id', 'product_name', 'variant_name', 'quantity', 'movement_type_display', 'reference', 'notes', 'created_at']
        read_only_fields = fields


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for PurchaseOrder model"""
    
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.IntegerField(write_only=True, required=True)
    created_by = UserPublicSerializer(read_only=True)
    items = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'po_number', 'supplier', 'created_by', 'items', 'status_display', 'total_cost')
    
    def get_items(self, obj):
        return [
            {
                'product_id': item.product.id,
                'product_name': item.product.name,
                'variant_id': item.variant.id if item.variant else None,
                'variant_name': item.variant.name if item.variant else None,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price
            }
            for item in obj.items.all()
        ]


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for purchase order lists"""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'supplier_name', 'status_display', 'item_count', 'total_cost', 'expected_delivery', 'created_at']
        read_only_fields = fields
    
    def get_item_count(self, obj):
        return obj.items.count()


class InventorySerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Inventory model"""
    
    product = ProductListSerializer(read_only=True)
    product_variant = ProductVariantSerializer(read_only=True)
    location = InventoryLocationSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True, allow_null=True)
    
    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'product', 'product_variant', 'location', 'supplier')


class InventoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for inventory lists"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='product_variant.name', read_only=True, allow_null=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'product_name', 'variant_name', 'location_name', 'quantity', 'reserved', 'reorder_level', 'last_updated']
        read_only_fields = fields


class InventoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating inventory"""
    
    class Meta:
        model = Inventory
        fields = ['quantity', 'reserved', 'reorder_level', 'low_stock_alert', 'notes']


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer for stock adjustments"""
    
    product_id = serializers.IntegerField(required=True)
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    location_id = serializers.IntegerField(required=True)
    adjustment = serializers.IntegerField(required=True)
    reason = serializers.CharField(required=True)
    reference = serializers.CharField(required=False, allow_blank=True)


class InventoryTransferSerializer(serializers.Serializer):
    """Serializer for inventory transfers between locations"""
    
    product_id = serializers.IntegerField(required=True)
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    from_location_id = serializers.IntegerField(required=True)
    to_location_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    reason = serializers.CharField(required=True)


class InventoryStatsSerializer(serializers.Serializer):
    """Serializer for inventory statistics"""
    
    total_products = serializers.IntegerField()
    total_variants = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    total_locations = serializers.IntegerField()
    total_suppliers = serializers.IntegerField()
    inventory_by_location = serializers.DictField()
    inventory_by_category = serializers.DictField()
    recent_movements = serializers.ListField(child=serializers.DictField())
