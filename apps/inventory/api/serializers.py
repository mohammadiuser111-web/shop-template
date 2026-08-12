"""
API serializers for Inventory app.
"""
from rest_framework import serializers
from ..models import Warehouse, Inventory, InventoryMovement, StockAlert, Supplier, PurchaseOrder, PurchaseOrderItem


# Warehouse Serializers
class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer for Warehouse."""
    
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class WarehouseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for warehouse list."""
    
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'code', 'city', 'state', 'country', 'phone', 'is_active', 'sort_order']
        read_only_fields = ['id', 'code']


# Inventory Serializers
class InventorySerializer(serializers.ModelSerializer):
    """Serializer for Inventory."""
    
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    variant = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    warehouse = WarehouseListSerializer(read_only=True)
    available_quantity = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    is_out_of_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ['id', 'product', 'variant', 'warehouse', 'created_at', 'updated_at']
    
    def get_available_quantity(self, obj):
        return obj.get_available_quantity()
    
    def get_is_low_stock(self, obj):
        return obj.is_low_stock()
    
    def get_is_out_of_stock(self, obj):
        return obj.is_out_of_stock()


class InventoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for inventory list."""
    
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    variant = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    warehouse = WarehouseListSerializer(read_only=True)
    available_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'variant', 'warehouse', 'quantity', 'reserved_quantity', 
                 'available_quantity', 'location', 'is_active']
        read_only_fields = ['id', 'product', 'variant', 'warehouse']
    
    def get_available_quantity(self, obj):
        return obj.get_available_quantity()


class InventoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating inventory record."""
    
    class Meta:
        model = Inventory
        fields = ['product', 'variant', 'warehouse', 'quantity', 'reserved_quantity', 
                 'location', 'low_stock_threshold', 'is_active']


class InventoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating inventory."""
    
    class Meta:
        model = Inventory
        fields = ['quantity', 'reserved_quantity', 'location', 'low_stock_threshold', 'is_active']


class InventoryStockUpdateSerializer(serializers.Serializer):
    """Serializer for updating inventory stock."""
    
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField()
    quantity_change = serializers.IntegerField()
    reason = serializers.CharField(required=False, default='')


# Inventory Movement Serializers
class InventoryMovementSerializer(serializers.ModelSerializer):
    """Serializer for InventoryMovement."""
    
    inventory = InventoryListSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = InventoryMovement
        fields = '__all__'
        read_only_fields = ['id', 'inventory', 'quantity_after', 'user', 'created_at']


class InventoryMovementListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for inventory movement list."""
    
    inventory = InventoryListSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = InventoryMovement
        fields = ['id', 'inventory', 'movement_type', 'quantity', 'quantity_after', 
                 'reference_type', 'reference_id', 'user', 'notes', 'created_at']
        read_only_fields = ['id', 'inventory', 'quantity_after', 'user', 'created_at']


# Stock Alert Serializers
class StockAlertSerializer(serializers.ModelSerializer):
    """Serializer for StockAlert."""
    
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    variant = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    warehouse = WarehouseListSerializer(read_only=True)
    notified_to = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = StockAlert
        fields = '__all__'
        read_only_fields = ['id', 'product', 'variant', 'warehouse', 'created_at', 'updated_at']


class StockAlertListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for stock alert list."""
    
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    variant = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    warehouse = WarehouseListSerializer(read_only=True)
    
    class Meta:
        model = StockAlert
        fields = ['id', 'product', 'variant', 'warehouse', 'alert_type', 'threshold', 
                 'current_quantity', 'is_notified', 'notified_at', 'created_at']
        read_only_fields = ['id', 'product', 'variant', 'warehouse', 'created_at']


# Supplier Serializers
class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier."""
    
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SupplierListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for supplier list."""
    
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'code', 'contact_person', 'phone', 'email', 'city', 
                 'state', 'country', 'is_active']
        read_only_fields = ['id', 'code']


# Purchase Order Serializers
class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrderItem."""
    
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    variant = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    purchase_order = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'
        read_only_fields = ['id', 'purchase_order', 'product', 'variant', 'subtotal', 'created_at', 'updated_at']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder."""
    
    supplier = SupplierListSerializer(read_only=True)
    warehouse = WarehouseListSerializer(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    approved_by = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['id', 'po_number', 'supplier', 'warehouse', 'subtotal', 'tax', 
                           'shipping_cost', 'total', 'created_by', 'approved_by', 'created_at', 'updated_at']


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for purchase order list."""
    
    supplier = SupplierListSerializer(read_only=True)
    warehouse = WarehouseListSerializer(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'supplier', 'warehouse', 'status', 'order_date', 
                 'expected_delivery_date', 'received_date', 'subtotal', 'tax', 'shipping_cost', 
                 'total', 'created_by', 'created_at']
        read_only_fields = ['id', 'po_number', 'subtotal', 'tax', 'shipping_cost', 'total', 'created_at']


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating purchase order."""
    
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'warehouse', 'status', 'order_date', 'expected_delivery_date',
                 'shipping_cost', 'notes', 'internal_notes']


class PurchaseOrderItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating purchase order item."""
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'variant', 'quantity', 'unit_price', 'notes']


# Inventory Statistics Serializer
class InventoryStatisticsSerializer(serializers.Serializer):
    """Serializer for inventory statistics."""
    
    total_warehouses = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_suppliers = serializers.IntegerField()
    total_purchase_orders = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    out_of_stock_count = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=12, decimal_places=2)
