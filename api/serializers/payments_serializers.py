"""
Payments Serializers
Serializers for payment models: PaymentMethod, PaymentTransaction, Wallet, WalletTransaction
"""

from rest_framework import serializers
from apps.payments.models import (
    PaymentMethod, PaymentTransaction, Wallet, WalletTransaction, Refund
)
from apps.orders.models import Order
from .accounts_serializers import UserPublicSerializer


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model"""
    
    logo_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'code', 'slug')
    
    def get_logo_url(self, obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None


class PaymentMethodListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for payment method lists"""
    
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'code', 'is_active', 'position', 'created_at']
        read_only_fields = fields


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet model"""
    
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user', 'currency')


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for WalletTransaction model"""
    
    wallet = WalletSerializer(read_only=True)
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'wallet', 'user', 'balance_after')


class WalletTransactionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for wallet transaction lists"""
    
    transaction_type = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = ['id', 'amount', 'transaction_type', 'description', 'created_at']
        read_only_fields = fields


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for Refund model"""
    
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    payment_transaction = serializers.PrimaryKeyRelatedField(
        queryset=PaymentTransaction.objects.all(),
        required=False,
        allow_null=True
    )
    processed_by = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Refund
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'refund_id', 'status', 'processed_by', 'processed_at')


class RefundListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for refund lists"""
    
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer = serializers.StringField(source='order.user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Refund
        fields = ['id', 'refund_id', 'order_id', 'order_number', 'customer', 'amount', 'reason', 'status_display', 'created_at']
        read_only_fields = fields


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for PaymentTransaction model"""
    
    payment_method = PaymentMethodSerializer(read_only=True)
    payment_method_id = serializers.IntegerField(write_only=True, required=True)
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    user = UserPublicSerializer(read_only=True)
    wallet = WalletSerializer(read_only=True, allow_null=True)
    
    class Meta:
        model = PaymentTransaction
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'transaction_id', 'status', 'user', 'wallet')


class PaymentTransactionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for payment transaction lists"""
    
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    payment_method = serializers.StringField(source='payment_method.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'transaction_id', 'order_id', 'order_number', 'payment_method', 'amount', 'currency', 'status_display', 'created_at']
        read_only_fields = fields


class PaymentTransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment transactions"""
    
    payment_method_id = serializers.IntegerField(required=True)
    order_id = serializers.IntegerField(required=True)
    
    class Meta:
        model = PaymentTransaction
        fields = ['payment_method_id', 'order_id', 'amount', 'currency', 'gateway_response', 'payment_data']


class PaymentVerifySerializer(serializers.Serializer):
    """Serializer for verifying payment transactions"""
    
    transaction_id = serializers.CharField(required=True)
    gateway = serializers.CharField(required=True)
    verification_data = serializers.DictField(required=True)


class PaymentCallbackSerializer(serializers.Serializer):
    """Serializer for payment gateway callbacks"""
    
    transaction_id = serializers.CharField(required=True)
    status = serializers.CharField(required=True)
    gateway = serializers.CharField(required=True)
    callback_data = serializers.DictField(required=True)


class PaymentStatsSerializer(serializers.Serializer):
    """Serializer for payment statistics"""
    
    total_transactions = serializers.IntegerField()
    successful_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    payment_methods = serializers.DictField()
    recent_transactions = serializers.ListField(child=serializers.DictField())
    wallet_balance = serializers.DecimalField(max_digits=15, decimal_places=2)


class PaymentGatewayConfigSerializer(serializers.Serializer):
    """Serializer for payment gateway configuration"""
    
    gateway = serializers.CharField(required=True)
    is_enabled = serializers.BooleanField(required=True)
    config = serializers.DictField(required=True)
