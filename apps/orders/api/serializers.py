"""
Serializers for Orders API.
"""
from rest_framework import serializers
from ..models import Order, OrderItem, Refund


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.SlugField(source='product.slug', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True, allow_null=True)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'variant', 'product_name', 'product_slug',
            'variant_name', 'product_image', 'quantity', 'price', 'total_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order', 'product_name', 'product_slug', 'variant_name', 'product_image', 'price', 'total_price', 'created_at', 'updated_at']
    
    def get_product_image(self, obj):
        """Get product primary image URL."""
        if obj.product and hasattr(obj.product, 'images') and obj.product.images.filter(is_primary=True).exists():
            image = obj.product.images.filter(is_primary=True).first()
            if image and image.image:
                if 'request' in self.context:
                    return self.context['request'].build_absolute_uri(image.image.url)
        return None


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for Refund model."""
    
    class Meta:
        model = Refund
        fields = [
            'id', 'order', 'amount', 'reason', 'status',
            'processed_by', 'processed_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order', 'processed_by', 'processed_at', 'created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'subtotal', 'tax',
            'shipping_cost', 'discount', 'total_amount', 'currency',
            'shipping_address', 'billing_address', 'payment_method',
            'shipping_method', 'coupon', 'notes', 'is_paid', 'is_shipped',
            'is_delivered', 'is_cancelled', 'cancelled_reason',
            'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'subtotal', 'tax', 'shipping_cost', 'discount', 'total_amount', 'is_paid', 'is_shipped', 'is_delivered', 'created_at', 'updated_at', 'items']


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Order."""
    
    user = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'subtotal', 'tax',
            'shipping_cost', 'discount', 'total_amount', 'currency',
            'shipping_address', 'billing_address', 'payment_method',
            'shipping_method', 'coupon', 'notes', 'is_paid', 'is_shipped',
            'is_delivered', 'is_cancelled', 'cancelled_reason',
            'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'subtotal', 'tax', 'shipping_cost', 'discount', 'total_amount', 'is_paid', 'is_shipped', 'is_delivered', 'created_at', 'updated_at', 'items']
    
    def get_user(self, obj):
        """Get user data."""
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name
            }
        return None


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating an order."""
    
    shipping_address_id = serializers.UUIDField(required=True)
    billing_address_id = serializers.UUIDField(required=False, allow_null=True)
    payment_method = serializers.CharField(required=True)
    shipping_method = serializers.CharField(required=True)
    coupon_code = serializers.CharField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True)
    
    class Meta:
        fields = ['shipping_address_id', 'billing_address_id', 'payment_method', 'shipping_method', 'coupon_code', 'notes']


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order."""
    
    class Meta:
        model = Order
        fields = ['status', 'notes', 'shipping_method', 'payment_method']


class OrderCancelSerializer(serializers.Serializer):
    """Serializer for cancelling an order."""
    
    reason = serializers.CharField(required=True)
    
    class Meta:
        fields = ['reason']


class OrderStatusSerializer(serializers.Serializer):
    """Serializer for order status update."""
    
    status = serializers.CharField(required=True)
    notes = serializers.CharField(required=False, allow_null=True)
    
    class Meta:
        fields = ['status', 'notes']
