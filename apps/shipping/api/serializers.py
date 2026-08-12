"""
API serializers for Shipping app.
"""
from rest_framework import serializers
from ..models import ShippingZone, ShippingZoneLocation, ShippingMethod, ShippingClass, PickupLocation


# Shipping Zone Serializers
class ShippingZoneSerializer(serializers.ModelSerializer):
    """Serializer for ShippingZone."""
    
    class Meta:
        model = ShippingZone
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShippingZoneListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for shipping zone list."""
    
    class Meta:
        model = ShippingZone
        fields = ['id', 'name', 'description', 'is_active', 'sort_order']
        read_only_fields = ['id']


# Shipping Zone Location Serializers
class ShippingZoneLocationSerializer(serializers.ModelSerializer):
    """Serializer for ShippingZoneLocation."""
    
    zone = ShippingZoneListSerializer(read_only=True)
    
    class Meta:
        model = ShippingZoneLocation
        fields = '__all__'
        read_only_fields = ['id', 'zone', 'created_at', 'updated_at']


class ShippingZoneLocationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating shipping zone location."""
    
    class Meta:
        model = ShippingZoneLocation
        fields = ['zone', 'location_type', 'location_code', 'location_name']


# Shipping Method Serializers
class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for ShippingMethod."""
    
    zone = ShippingZoneListSerializer(read_only=True)
    
    class Meta:
        model = ShippingMethod
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'zone', 'created_at', 'updated_at']


class ShippingMethodListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for shipping method list."""
    
    zone = ShippingZoneListSerializer(read_only=True)
    
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'slug', 'description', 'zone', 'pricing_type', 'base_price',
                 'estimated_delivery_min', 'estimated_delivery_max', 'is_active', 'is_free', 'logo']
        read_only_fields = ['id', 'slug', 'zone']


class ShippingMethodCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating shipping method."""
    
    class Meta:
        model = ShippingMethod
        fields = ['name', 'slug', 'description', 'zone', 'pricing_type', 'base_price',
                 'price_per_kg', 'price_per_item', 'percentage', 'min_order_amount',
                 'max_order_amount', 'estimated_delivery_min', 'estimated_delivery_max',
                 'is_active', 'is_free', 'sort_order', 'logo']


class ShippingMethodCostSerializer(serializers.Serializer):
    """Serializer for shipping method cost calculation."""
    
    order_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    item_count = serializers.IntegerField(default=0)
    total_weight = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    cart_items = serializers.JSONField(required=False, default=list)


class ShippingMethodCostResponseSerializer(serializers.Serializer):
    """Serializer for shipping method cost response."""
    
    method_id = serializers.UUIDField()
    method_name = serializers.CharField()
    cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    estimated_delivery = serializers.CharField()
    is_available = serializers.BooleanField()
    message = serializers.CharField(required=False, default='')


# Shipping Class Serializers
class ShippingClassSerializer(serializers.ModelSerializer):
    """Serializer for ShippingClass."""
    
    class Meta:
        model = ShippingClass
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShippingClassListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for shipping class list."""
    
    class Meta:
        model = ShippingClass
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id', 'slug']


# Pickup Location Serializers
class PickupLocationSerializer(serializers.ModelSerializer):
    """Serializer for PickupLocation."""
    
    class Meta:
        model = PickupLocation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PickupLocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for pickup location list."""
    
    class Meta:
        model = PickupLocation
        fields = ['id', 'name', 'address', 'city', 'state', 'postal_code', 'country',
                 'phone', 'email', 'opening_hours', 'is_active', 'sort_order']
        read_only_fields = ['id']


# Shipping Statistics Serializer
class ShippingStatisticsSerializer(serializers.Serializer):
    """Serializer for shipping statistics."""
    
    total_zones = serializers.IntegerField()
    total_methods = serializers.IntegerField()
    total_pickup_locations = serializers.IntegerField()
    active_methods = serializers.IntegerField()
    average_shipping_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
