"""
Shipping Serializers
Serializers for shipping models: ShippingMethod, ShippingZone, ShippingClass, PickupLocation, DeliveryTime
"""

from rest_framework import serializers
from apps.shipping.models import (
    ShippingMethod, ShippingZone, ShippingClass, 
    PickupLocation, DeliveryTime, ShippingRate
)
from .core_serializers import CountrySerializer


class ShippingZoneSerializer(serializers.ModelSerializer):
    """Serializer for ShippingZone model"""
    
    countries = CountrySerializer(many=True, read_only=True)
    country_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ShippingZone
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug')


class ShippingClassSerializer(serializers.ModelSerializer):
    """Serializer for ShippingClass model"""
    
    class Meta:
        model = ShippingClass
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug')


class PickupLocationSerializer(serializers.ModelSerializer):
    """Serializer for PickupLocation model"""
    
    address = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PickupLocation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug')
    
    def get_address(self, obj):
        return obj.get_full_address()


class DeliveryTimeSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryTime model"""
    
    class Meta:
        model = DeliveryTime
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class ShippingRateSerializer(serializers.ModelSerializer):
    """Serializer for ShippingRate model"""
    
    shipping_method = serializers.StringField(source='shipping_method.name', read_only=True)
    shipping_zone = serializers.StringField(source='shipping_zone.name', read_only=True)
    shipping_class = serializers.StringField(source='shipping_class.name', read_only=True, allow_null=True)
    
    class Meta:
        model = ShippingRate
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'shipping_method', 'shipping_zone', 'shipping_class')


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for ShippingMethod model"""
    
    zones = ShippingZoneSerializer(many=True, read_only=True)
    rates = ShippingRateSerializer(many=True, read_only=True)
    pickup_locations = PickupLocationSerializer(many=True, read_only=True)
    delivery_times = DeliveryTimeSerializer(many=True, read_only=True)
    
    class Meta:
        model = ShippingMethod
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug', 'zones', 'rates', 'pickup_locations', 'delivery_times')


class ShippingMethodListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for shipping method lists"""
    
    zone_count = serializers.SerializerMethodField(read_only=True)
    rate_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'code', 'description', 'is_active', 'zone_count', 'rate_count', 'created_at']
        read_only_fields = fields
    
    def get_zone_count(self, obj):
        return obj.zones.count()
    
    def get_rate_count(self, obj):
        return obj.rates.count()


class ShippingMethodCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating shipping methods"""
    
    zone_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ShippingMethod
        fields = ['name', 'code', 'description', 'is_active', 'tracking_url', 'zone_ids']


class ShippingMethodUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating shipping methods"""
    
    zone_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ShippingMethod
        fields = ['name', 'code', 'description', 'is_active', 'tracking_url', 'zone_ids']


class ShippingRateCreateSerializer(serializers.Serializer):
    """Serializer for creating shipping rates"""
    
    shipping_method_id = serializers.IntegerField(required=True)
    shipping_zone_id = serializers.IntegerField(required=True)
    shipping_class_id = serializers.IntegerField(required=False, allow_null=True)
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    price_per_kg = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    price_per_item = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    min_order_value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    max_order_value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    min_weight = serializers.FloatField(required=False, allow_null=True)
    max_weight = serializers.FloatField(required=False, allow_null=True)
    estimated_delivery_min = serializers.IntegerField(required=False, allow_null=True)
    estimated_delivery_max = serializers.IntegerField(required=False, allow_null=True)


class ShippingCalculatorSerializer(serializers.Serializer):
    """Serializer for shipping cost calculation"""
    
    shipping_method_id = serializers.IntegerField(required=True)
    shipping_zone_id = serializers.IntegerField(required=False, allow_null=True)
    destination_country = serializers.CharField(required=False, allow_blank=True)
    destination_zip = serializers.CharField(required=False, allow_blank=True)
    total_weight = serializers.FloatField(required=True)
    item_count = serializers.IntegerField(required=True)
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)


class ShippingCostResultSerializer(serializers.Serializer):
    """Serializer for shipping cost calculation results"""
    
    shipping_method = serializers.DictField()
    available_methods = serializers.ListField(child=serializers.DictField())
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    estimated_delivery = serializers.CharField()
    pickup_locations = serializers.ListField(child=serializers.DictField())
