"""
Cart Serializers
Serializers for cart models: Cart, CartItem
"""

from rest_framework import serializers
from apps.cart.models import Cart, CartItem
from apps.products.models import Product, ProductVariant
from .products_serializers import ProductListSerializer, ProductVariantSerializer
from .discounts_serializers import CouponSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for CartItem model"""
    
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True, allow_null=True)
    product_id = serializers.IntegerField(write_only=True, required=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    final_price = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'cart', 'product', 'variant', 'subtotal', 'final_price')
    
    def get_subtotal(self, obj):
        return obj.subtotal
    
    def get_final_price(self, obj):
        return obj.final_price


class CartItemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for cart item lists"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True, allow_null=True)
    product_image = serializers.SerializerMethodField(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.price', read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product_name', 'product_slug', 'variant_name', 'product_image', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = fields
    
    def get_product_image(self, obj):
        if obj.product and obj.product.primary_image:
            return self.context['request'].build_absolute_uri(obj.product.primary_image.image.url)
        return None
    
    def get_subtotal(self, obj):
        return obj.subtotal


class CartItemCreateSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    
    product_id = serializers.IntegerField(required=True)
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(required=True, min_value=1, default=1)


class CartItemUpdateSerializer(serializers.Serializer):
    """Serializer for updating cart items"""
    
    quantity = serializers.IntegerField(required=True, min_value=1)


class CartSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Cart model"""
    
    items = CartItemSerializer(many=True, read_only=True)
    coupon = CouponSerializer(read_only=True, allow_null=True)
    item_count = serializers.SerializerMethodField(read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    discount_amount = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'session_key', 'user', 'items', 'item_count', 'subtotal', 'discount_amount', 'total', 'coupon')
    
    def get_item_count(self, obj):
        return obj.items.count()
    
    def get_subtotal(self, obj):
        return obj.subtotal
    
    def get_discount_amount(self, obj):
        return obj.discount_amount
    
    def get_total(self, obj):
        return obj.total


class CartListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for cart lists"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    item_count = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'cart_id', 'user_email', 'item_count', 'total', 'created_at', 'updated_at']
        read_only_fields = fields
    
    def get_item_count(self, obj):
        return obj.items.count()
    
    def get_total(self, obj):
        return obj.total


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    
    product_id = serializers.IntegerField(required=True)
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(required=True, min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    
    item_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)


class RemoveFromCartSerializer(serializers.Serializer):
    """Serializer for removing items from cart"""
    
    item_id = serializers.IntegerField(required=True)


class ClearCartSerializer(serializers.Serializer):
    """Serializer for clearing cart"""
    
    confirm = serializers.BooleanField(required=True, default=False)


class ApplyCouponSerializer(serializers.Serializer):
    """Serializer for applying coupon to cart"""
    
    coupon_code = serializers.CharField(required=True)


class RemoveCouponSerializer(serializers.Serializer):
    """Serializer for removing coupon from cart"""
    
    confirm = serializers.BooleanField(required=True, default=False)


class CartSummarySerializer(serializers.Serializer):
    """Serializer for cart summary"""
    
    cart_id = serializers.CharField()
    item_count = serializers.IntegerField()
    items = CartItemListSerializer(many=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_code = serializers.CharField(required=False, allow_blank=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2)
