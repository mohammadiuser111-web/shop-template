"""
API serializers for Discounts app.
"""
from rest_framework import serializers
from ..models import Discount, Coupon, Campaign, CouponUsage


# Discount Serializers
class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for Discount."""
    
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = ['id', 'uses_count', 'created_at', 'updated_at']


class DiscountListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for discount list."""
    
    class Meta:
        model = Discount
        fields = ['id', 'name', 'code', 'discount_type', 'discount_value', 
                 'is_active', 'start_date', 'end_date', 'max_uses', 'uses_count']
        read_only_fields = ['id', 'uses_count']


# Coupon Serializers
class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon."""
    
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    exclude_products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    exclude_categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    allowed_users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['id', 'uses_count', 'created_at', 'updated_at']


class CouponListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for coupon list."""
    
    class Meta:
        model = Coupon
        fields = ['id', 'name', 'code', 'coupon_type', 'discount_type', 'discount_value',
                 'is_active', 'start_date', 'end_date', 'min_order_amount', 'max_order_amount',
                 'max_uses', 'uses_count', 'max_uses_per_user', 'free_shipping']
        read_only_fields = ['id', 'uses_count']


class CouponCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating coupon."""
    
    class Meta:
        model = Coupon
        fields = ['name', 'code', 'coupon_type', 'discount_type', 'discount_value',
                 'is_active', 'start_date', 'end_date', 'min_order_amount', 'max_order_amount',
                 'max_uses', 'max_uses_per_user', 'description', 'free_shipping']


class CouponValidateSerializer(serializers.Serializer):
    """Serializer for validating a coupon."""
    
    code = serializers.CharField()
    order_id = serializers.IntegerField(required=False, allow_null=True)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    order_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)


class CouponValidateResponseSerializer(serializers.Serializer):
    """Serializer for coupon validation response."""
    
    is_valid = serializers.BooleanField()
    coupon_id = serializers.UUIDField(required=False, allow_null=True)
    code = serializers.CharField(required=False, allow_null=True)
    discount_type = serializers.CharField(required=False, allow_null=True)
    discount_value = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    message = serializers.CharField(required=False, default='')
    free_shipping = serializers.BooleanField(default=False)


# Campaign Serializers
class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaign."""
    
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['id', 'uses_count', 'created_at', 'updated_at']


class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for campaign list."""
    
    class Meta:
        model = Campaign
        fields = ['id', 'name', 'campaign_type', 'discount_type', 'discount_value',
                 'is_active', 'start_date', 'end_date', 'priority']
        read_only_fields = ['id']


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating campaign."""
    
    class Meta:
        model = Campaign
        fields = ['name', 'campaign_type', 'discount_type', 'discount_value',
                 'is_active', 'start_date', 'end_date', 'priority', 'description',
                 'bogo_quantity', 'bogo_discount_type', 'bogo_discount_value', 'tiers']


# Coupon Usage Serializers
class CouponUsageSerializer(serializers.ModelSerializer):
    """Serializer for CouponUsage."""
    
    coupon = CouponListSerializer(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = CouponUsage
        fields = '__all__'
        read_only_fields = ['id', 'coupon', 'order', 'user', 'discount_amount', 'created_at']


class CouponUsageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for coupon usage list."""
    
    coupon = CouponListSerializer(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = CouponUsage
        fields = ['id', 'coupon', 'order', 'user', 'discount_amount', 'created_at']
        read_only_fields = ['id', 'coupon', 'order', 'user', 'discount_amount', 'created_at']


# Discount Statistics Serializer
class DiscountStatisticsSerializer(serializers.Serializer):
    """Serializer for discount statistics."""
    
    total_coupons = serializers.IntegerField()
    total_campaigns = serializers.IntegerField()
    active_coupons = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    total_usage = serializers.IntegerField()
    total_discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
