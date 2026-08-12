"""
Serializers for Cart API.
"""
from rest_framework import serializers
from ..models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.SlugField(source='product.slug', read_only=True)
    product_image = serializers.SerializerMethodField()
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_sale_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'product_name', 'product_slug',
            'product_image', 'product_price', 'product_sale_price',
            'quantity', 'price', 'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'cart', 'product_name', 'product_slug', 'product_image', 'product_price', 'product_sale_price', 'price', 'total_price', 'created_at', 'updated_at']
    
    def get_product_image(self, obj):
        """Get product primary image URL."""
        if obj.product and obj.product.images.filter(is_primary=True).exists():
            image = obj.product.images.filter(is_primary=True).first()
            if image and image.image:
                return self.context['request'].build_absolute_uri(image.image.url)
        return None
    
    def get_product_sale_price(self, obj):
        """Get product sale price."""
        if obj.product:
            return obj.product.sale_price
        return None


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    
    items = CartItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'is_active', 'created_at', 'updated_at',
            'items', 'item_count', 'subtotal', 'total', 'discount', 'tax', 'grand_total'
        ]
        read_only_fields = ['id', 'session_key', 'is_active', 'created_at', 'updated_at', 'items', 'item_count', 'subtotal', 'total', 'discount', 'tax', 'grand_total']


class CartCreateSerializer(serializers.Serializer):
    """Serializer for creating a cart."""
    
    class Meta:
        fields = []


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding item to cart."""
    
    product_id = serializers.UUIDField(required=True)
    quantity = serializers.IntegerField(default=1, min_value=1)
    variant_id = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        fields = ['product_id', 'quantity', 'variant_id']


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item."""
    
    quantity = serializers.IntegerField(min_value=1)
    
    class Meta:
        fields = ['quantity']


class ApplyCouponSerializer(serializers.Serializer):
    """Serializer for applying coupon to cart."""
    
    coupon_code = serializers.CharField(required=True)
    
    class Meta:
        fields = ['coupon_code']
