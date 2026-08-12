"""
API serializers for Payments app.
"""
from rest_framework import serializers
from ..models import PaymentGateway, Transaction, Wallet, WalletTransaction


# Payment Gateway Serializers
class PaymentGatewaySerializer(serializers.ModelSerializer):
    """Serializer for PaymentGateway."""
    
    class Meta:
        model = PaymentGateway
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentGatewayListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for payment gateway list."""
    
    class Meta:
        model = PaymentGateway
        fields = ['id', 'name', 'gateway_type', 'title', 'description', 'logo', 'is_active', 'sort_order']
        read_only_fields = ['id']


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    """Serializer for payment gateway configuration."""
    
    class Meta:
        model = PaymentGateway
        fields = ['id', 'name', 'gateway_type', 'config', 'title', 'description', 'is_active']
        read_only_fields = ['id', 'gateway_type']


# Transaction Serializers
class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    refund = serializers.PrimaryKeyRelatedField(read_only=True)
    gateway = PaymentGatewayListSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'transaction_id', 'user', 'order', 'refund', 'gateway', 
                           'gateway_reference', 'gateway_response', 'created_at', 'updated_at', 
                           'completed_at', 'error_code', 'error_message']


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a transaction."""
    
    class Meta:
        model = Transaction
        fields = ['gateway', 'transaction_type', 'amount', 'currency', 'customer_name', 
                 'customer_email', 'customer_phone']


class TransactionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a transaction."""
    
    class Meta:
        model = Transaction
        fields = ['status', 'gateway_reference', 'gateway_response', 'error_code', 'error_message']


class TransactionVerifySerializer(serializers.Serializer):
    """Serializer for verifying a transaction."""
    
    transaction_id = serializers.CharField()
    gateway_reference = serializers.CharField(required=False)
    status = serializers.CharField(required=False)


# Wallet Serializers
class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for WalletTransaction."""
    
    wallet = WalletSerializer(read_only=True)
    transaction = TransactionSerializer(read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = '__all__'
        read_only_fields = ['id', 'wallet', 'balance_after', 'created_at']


class WalletTransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a wallet transaction."""
    
    class Meta:
        model = WalletTransaction
        fields = ['amount', 'transaction_type', 'description']


class WalletDepositSerializer(serializers.Serializer):
    """Serializer for wallet deposit."""
    
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    description = serializers.CharField(required=False, default='')


class WalletWithdrawSerializer(serializers.Serializer):
    """Serializer for wallet withdrawal."""
    
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    description = serializers.CharField(required=False, default='')


# Payment Statistics Serializer
class PaymentStatisticsSerializer(serializers.Serializer):
    """Serializer for payment statistics."""
    
    total_transactions = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    success_rate = serializers.FloatField()
    pending_count = serializers.IntegerField()
    success_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()
    refunded_count = serializers.IntegerField()
