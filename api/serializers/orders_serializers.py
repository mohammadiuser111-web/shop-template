"""
Orders Serializers
Serializers for order models: Order, OrderItem, Shipping, Payment
"""

from rest_framework import serializers
from apps.orders.models import Order, OrderItem, Shipping, OrderStatus
from apps.products.models import Product, ProductVariant
from apps.accounts.models import UserAddress
from .products_serializers import ProductListSerializer, ProductVariantSerializer
from .accounts_serializers import UserPublicSerializer, UserAddressSerializer
from .payments_serializers import PaymentTransactionListSerializer
from .shipping_serializers import ShippingMethodSerializer
from .discounts_serializers import CouponSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for OrderItem model"""
    
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True, allow_null=True)
    product_id = serializers.IntegerField(write_only=True, required=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    final_price = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'order', 'product', 'variant', 'subtotal', 'final_price')
    
    def get_subtotal(self, obj):
        return obj.subtotal
    
    def get_final_price(self, obj):
        return obj.final_price


class OrderItemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order item lists"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True, allow_null=True)
    product_image = serializers.SerializerMethodField(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_slug', 'variant_name', 'product_image', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = fields
    
    def get_product_image(self, obj):
        if obj.product and obj.product.primary_image:
            return self.context['request'].build_absolute_uri(obj.product.primary_image.image.url)
        return None
    
    def get_subtotal(self, obj):
        return obj.subtotal


class ShippingSerializer(serializers.ModelSerializer):
    """Serializer for Shipping model"""
    
    shipping_method = ShippingMethodSerializer(read_only=True)
    shipping_method_id = serializers.IntegerField(write_only=True, required=True)
    shipping_address = UserAddressSerializer(read_only=True)
    shipping_address_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Shipping
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'order', 'shipping_method', 'shipping_address', 'tracking_number')


class ShippingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for shipping lists"""
    
    shipping_method_name = serializers.CharField(source='shipping_method.name', read_only=True)
    tracking_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Shipping
        fields = ['id', 'shipping_method_name', 'tracking_number', 'tracking_url', 'cost', 'estimated_delivery', 'delivered_at']
        read_only_fields = fields
    
    def get_tracking_url(self, obj):
        if obj.shipping_method and obj.shipping_method.tracking_url and obj.tracking_number:
            return obj.shipping_method.tracking_url.replace('{tracking_number}', obj.tracking_number)
        return None


class OrderSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Order model"""
    
    user = UserPublicSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    shipping = ShippingSerializer(read_only=True)
    coupon = CouponSerializer(read_only=True, allow_null=True)
    payments = PaymentTransactionListSerializer(many=True, read_only=True)
    status_history = serializers.SerializerMethodField(read_only=True)
    item_count = serializers.SerializerMethodField(read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    discount_amount = serializers.SerializerMethodField(read_only=True)
    shipping_cost = serializers.SerializerMethodField(read_only=True)
    tax_amount = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'order_number', 'user', 'items', 
            'shipping', 'coupon', 'payments', 'status_history', 'item_count',
            'subtotal', 'discount_amount', 'shipping_cost', 'tax_amount', 'total',
            'status_display', 'payment_status_display'
        )
    
    def get_status_history(self, obj):
        return [
            {
                'status': status.status,
                'status_display': status.get_status_display(),
                'created_at': status.created_at,
                'notes': status.notes
            }
            for status in obj.status_history.all().order_by('created_at')
        ]
    
    def get_item_count(self, obj):
        return obj.items.count()
    
    def get_subtotal(self, obj):
        return obj.subtotal
    
    def get_discount_amount(self, obj):
        return obj.discount_amount
    
    def get_shipping_cost(self, obj):
        return obj.shipping_cost
    
    def get_tax_amount(self, obj):
        return obj.tax_amount
    
    def get_total(self, obj):
        return obj.total


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order lists"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    item_count = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user_email', 'item_count', 'total', 'status_display', 'payment_status_display', 'created_at', 'updated_at']
        read_only_fields = fields
    
    def get_item_count(self, obj):
        return obj.items.count()
    
    def get_total(self, obj):
        return obj.total


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders from cart"""
    
    cart_id = serializers.CharField(required=True)
    shipping_method_id = serializers.IntegerField(required=True)
    shipping_address_id = serializers.IntegerField(required=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating orders"""
    
    class Meta:
        model = Order
        fields = ['notes', 'shipping_notes']


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    
    status = serializers.ChoiceField(
        choices=['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded', 'failed'],
        required=True
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    notify_customer = serializers.BooleanField(required=False, default=True)


class OrderCancelSerializer(serializers.Serializer):
    """Serializer for cancelling orders"""
    
    reason = serializers.CharField(required=True)
    refund_requested = serializers.BooleanField(required=False, default=False)


class OrderRefundSerializer(serializers.Serializer):
    """Serializer for requesting order refunds"""
    
    order_id = serializers.IntegerField(required=True)
    items = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    reason = serializers.CharField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class OrderStatsSerializer(serializers.Serializer):
    """Serializer for order statistics"""
    
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    processing_orders = serializers.IntegerField()
    shipped_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders_by_date = serializers.DictField()
    orders_by_status = serializers.DictField()
    recent_orders = serializers.ListField(child=serializers.DictField())
    top_products = serializers.ListField(child=serializers.DictField())


class OrderExportSerializer(serializers.Serializer):
    """Serializer for exporting orders"""
    
    format = serializers.ChoiceField(choices=['csv', 'excel', 'json'], default='csv')
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    status = serializers.CharField(required=False, allow_blank=True)
    payment_status = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.IntegerField(required=False, allow_null=True)
