"""
Discounts Serializers
Serializers for discount models: Coupon, Discount, PriceRule, CouponUsage
"""

from rest_framework import serializers
from apps.discounts.models import Coupon, Discount, PriceRule, CouponUsage
from .products_serializers import CategorySerializer, BrandSerializer, ProductListSerializer
from .accounts_serializers import UserPublicSerializer


class CategorySerializerForDiscount(serializers.ModelSerializer):
    """Simplified category serializer for discounts"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class BrandSerializerForDiscount(serializers.ModelSerializer):
    """Simplified brand serializer for discounts"""
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug']


class ProductListSerializerForDiscount(serializers.ModelSerializer):
    """Simplified product serializer for discounts"""
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price']


class PriceRuleSerializer(serializers.ModelSerializer):
    """Serializer for PriceRule model"""
    
    class Meta:
        model = PriceRule
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'rule_id', 'slug')


class PriceRuleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for price rule lists"""
    
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    customer_selection_display = serializers.CharField(source='get_customer_selection_display', read_only=True)
    target_selection_display = serializers.CharField(source='get_target_selection_display', read_only=True)
    
    class Meta:
        model = PriceRule
        fields = ['id', 'rule_id', 'name', 'discount_type', 'discount_type_display', 'value', 'customer_selection', 'customer_selection_display', 'target_selection', 'target_selection_display', 'is_active', 'starts_at', 'ends_at', 'created_at']
        read_only_fields = fields


class CouponSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Coupon model"""
    
    price_rule = PriceRuleSerializer(read_only=True)
    price_rule_id = serializers.IntegerField(write_only=True, required=True)
    applicable_categories = CategorySerializerForDiscount(many=True, read_only=True)
    applicable_brands = BrandSerializerForDiscount(many=True, read_only=True)
    applicable_products = ProductListSerializerForDiscount(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    brand_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    usage_count = serializers.SerializerMethodField(read_only=True)
    is_valid = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'code', 'price_rule', 'usage_count', 'is_valid', 'applicable_categories', 'applicable_brands', 'applicable_products')
    
    def get_usage_count(self, obj):
        return CouponUsage.objects.filter(coupon=obj).count()
    
    def get_is_valid(self, obj):
        return obj.is_valid()


class CouponListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for coupon lists"""
    
    price_rule_name = serializers.CharField(source='price_rule.name', read_only=True)
    discount_type = serializers.CharField(source='price_rule.discount_type', read_only=True)
    discount_value = serializers.CharField(source='price_rule.value', read_only=True)
    usage_count = serializers.SerializerMethodField(read_only=True)
    is_valid = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'price_rule_name', 'discount_type', 'discount_value', 'usage_limit', 'usage_count', 'is_active', 'is_valid', 'starts_at', 'ends_at', 'created_at']
        read_only_fields = fields
    
    def get_usage_count(self, obj):
        return CouponUsage.objects.filter(coupon=obj).count()
    
    def get_is_valid(self, obj):
        return obj.is_valid()


class CouponCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating coupons"""
    
    price_rule_id = serializers.IntegerField(required=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    brand_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = Coupon
        fields = ['code', 'price_rule_id', 'usage_limit', 'per_customer_limit', 'starts_at', 'ends_at', 'is_active', 'category_ids', 'brand_ids', 'product_ids', 'minimum_order_value', 'maximum_discount_amount']


class CouponUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating coupons"""
    
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    brand_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = Coupon
        fields = ['usage_limit', 'per_customer_limit', 'starts_at', 'ends_at', 'is_active', 'category_ids', 'brand_ids', 'product_ids', 'minimum_order_value', 'maximum_discount_amount']


class CouponUsageSerializer(serializers.ModelSerializer):
    """Serializer for CouponUsage model"""
    
    coupon = CouponListSerializer(read_only=True)
    user = UserPublicSerializer(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'coupon', 'user', 'order')


class CouponUsageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for coupon usage lists"""
    
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        model = CouponUsage
        fields = ['id', 'coupon_code', 'user_email', 'order_id', 'discount_amount', 'created_at']
        read_only_fields = fields


class DiscountSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Discount model"""
    
    price_rule = PriceRuleSerializer(read_only=True)
    applicable_categories = CategorySerializerForDiscount(many=True, read_only=True)
    applicable_brands = BrandSerializerForDiscount(many=True, read_only=True)
    applicable_products = ProductListSerializerForDiscount(many=True, read_only=True)
    
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'price_rule', 'applicable_categories', 'applicable_brands', 'applicable_products')


class DiscountListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for discount lists"""
    
    price_rule_name = serializers.CharField(source='price_rule.name', read_only=True)
    discount_type = serializers.CharField(source='price_rule.discount_type', read_only=True)
    discount_value = serializers.CharField(source='price_rule.value', read_only=True)
    
    class Meta:
        model = Discount
        fields = ['id', 'name', 'price_rule_name', 'discount_type', 'discount_value', 'is_active', 'starts_at', 'ends_at', 'created_at']
        read_only_fields = fields


class CouponValidateSerializer(serializers.Serializer):
    """Serializer for validating coupons"""
    
    coupon_code = serializers.CharField(required=True)
    cart_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )


class CouponValidationResultSerializer(serializers.Serializer):
    """Serializer for coupon validation results"""
    
    is_valid = serializers.BooleanField()
    coupon = CouponSerializer()
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    error = serializers.CharField(required=False, allow_blank=True)


class DiscountCalculatorSerializer(serializers.Serializer):
    """Serializer for calculating discounts"""
    
    product_id = serializers.IntegerField(required=False, allow_null=True)
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    brand_id = serializers.IntegerField(required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    quantity = serializers.IntegerField(required=True, default=1)
    user_id = serializers.IntegerField(required=False, allow_null=True)


class DiscountStatsSerializer(serializers.Serializer):
    """Serializer for discount statistics"""
    
    total_coupons = serializers.IntegerField()
    active_coupons = serializers.IntegerField()
    total_discounts = serializers.IntegerField()
    active_discounts = serializers.IntegerField()
    total_usage = serializers.IntegerField()
    total_discount_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    most_used_coupons = serializers.ListField(child=serializers.DictField())
    recent_usage = serializers.ListField(child=serializers.DictField())
