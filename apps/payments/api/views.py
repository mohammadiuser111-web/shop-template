"""
API views for Payments app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import uuid

from ..models import PaymentGateway, Transaction, Wallet, WalletTransaction
from apps.orders.models import Order, Refund
from .serializers import (
    PaymentGatewaySerializer, PaymentGatewayListSerializer, PaymentGatewayConfigSerializer,
    TransactionSerializer, TransactionCreateSerializer, TransactionUpdateSerializer,
    TransactionVerifySerializer, WalletSerializer, WalletTransactionSerializer,
    WalletDepositSerializer, WalletWithdrawSerializer, PaymentStatisticsSerializer
)


# Payment Gateway Views
class PaymentGatewayListAPIView(generics.ListAPIView):
    """List payment gateways."""
    
    serializer_class = PaymentGatewayListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get active payment gateways."""
        return PaymentGateway.objects.filter(is_active=True).order_by('sort_order', 'name')


class PaymentGatewayRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve payment gateway."""
    
    serializer_class = PaymentGatewaySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = PaymentGateway.objects.all()


class PaymentGatewayCreateAPIView(generics.CreateAPIView):
    """Create payment gateway."""
    
    serializer_class = PaymentGatewaySerializer
    permission_classes = [permissions.IsAdminUser]


class PaymentGatewayUpdateAPIView(generics.UpdateAPIView):
    """Update payment gateway."""
    
    serializer_class = PaymentGatewayConfigSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = PaymentGateway.objects.all()


class PaymentGatewayDestroyAPIView(generics.DestroyAPIView):
    """Delete payment gateway."""
    
    serializer_class = PaymentGatewaySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = PaymentGateway.objects.all()


# Transaction Views
class TransactionListAPIView(generics.ListAPIView):
    """List transactions."""
    
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get transactions."""
        if self.request.user.is_superuser:
            return Transaction.objects.all().order_by('-created_at')
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')


class TransactionRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve transaction."""
    
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get transactions."""
        if self.request.user.is_superuser:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=self.request.user)


class TransactionCreateAPIView(views.APIView):
    """Create a transaction."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """Create transaction."""
        serializer = TransactionCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate transaction ID
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        # Get gateway
        gateway = None
        if serializer.validated_data.get('gateway'):
            gateway = get_object_or_404(PaymentGateway, pk=serializer.validated_data['gateway'])
        
        # Create transaction
        transaction_obj = Transaction.objects.create(
            transaction_id=transaction_id,
            user=request.user,
            gateway=gateway,
            transaction_type=serializer.validated_data['transaction_type'],
            amount=serializer.validated_data['amount'],
            currency=serializer.validated_data.get('currency', 'IRR'),
            customer_name=serializer.validated_data.get('customer_name', request.user.get_full_name() or ''),
            customer_email=serializer.validated_data.get('customer_email', request.user.email or ''),
            customer_phone=serializer.validated_data.get('customer_phone', '')
        )
        
        serializer = TransactionSerializer(transaction_obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionUpdateAPIView(generics.UpdateAPIView):
    """Update transaction."""
    
    serializer_class = TransactionUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Transaction.objects.all()


class TransactionVerifyAPIView(views.APIView):
    """Verify a transaction."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Verify transaction."""
        serializer = TransactionVerifySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        transaction_id = serializer.validated_data['transaction_id']
        transaction_obj = get_object_or_404(Transaction, transaction_id=transaction_id)
        
        # Check if user can verify this transaction
        if not request.user.is_superuser and transaction_obj.user != request.user:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Update transaction status
        if serializer.validated_data.get('status'):
            transaction_obj.status = serializer.validated_data['status']
        
        if serializer.validated_data.get('gateway_reference'):
            transaction_obj.gateway_reference = serializer.validated_data['gateway_reference']
        
        transaction_obj.completed_at = timezone.now()
        transaction_obj.save()
        
        serializer = TransactionSerializer(transaction_obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Wallet Views
class WalletRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve wallet."""
    
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get user's wallet."""
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class WalletTransactionListAPIView(generics.ListAPIView):
    """List wallet transactions."""
    
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get wallet transactions."""
        wallet = Wallet.objects.filter(user=self.request.user).first()
        if wallet:
            return WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')
        return WalletTransaction.objects.none()


class WalletDepositAPIView(views.APIView):
    """Deposit to wallet."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """Deposit to wallet."""
        serializer = WalletDepositSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')
        
        wallet.add_balance(amount, description)
        
        serializer = WalletSerializer(wallet, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletWithdrawAPIView(views.APIView):
    """Withdraw from wallet."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """Withdraw from wallet."""
        serializer = WalletWithdrawSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')
        
        try:
            wallet.subtract_balance(amount, description)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = WalletSerializer(wallet, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Payment Statistics View
class PaymentStatisticsAPIView(views.APIView):
    """Get payment statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Return payment statistics."""
        from django.db.models import Count, Sum, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        # Today
        today = timezone.now().date()
        today_transactions = Transaction.objects.filter(created_at__date=today)
        
        # This week
        week_start = today - timedelta(days=today.weekday())
        week_transactions = Transaction.objects.filter(created_at__date__gte=week_start)
        
        # This month
        month_start = today.replace(day=1)
        month_transactions = Transaction.objects.filter(created_at__date__gte=month_start)
        
        # All time
        all_transactions = Transaction.objects.all()
        
        # Calculate success rate
        total_count = all_transactions.count()
        success_count = all_transactions.filter(status='success').count()
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        data = {
            'total_transactions': total_count,
            'total_amount': all_transactions.aggregate(total=Sum('amount'))['total'] or 0,
            'success_rate': round(success_rate, 2),
            'pending_count': all_transactions.filter(status='pending').count(),
            'success_count': success_count,
            'failed_count': all_transactions.filter(status='failed').count(),
            'cancelled_count': all_transactions.filter(status='cancelled').count(),
            'refunded_count': all_transactions.filter(status='refunded').count(),
            'today': {
                'count': today_transactions.count(),
                'amount': today_transactions.aggregate(total=Sum('amount'))['total'] or 0
            },
            'this_week': {
                'count': week_transactions.count(),
                'amount': week_transactions.aggregate(total=Sum('amount'))['total'] or 0
            },
            'this_month': {
                'count': month_transactions.count(),
                'amount': month_transactions.aggregate(total=Sum('amount'))['total'] or 0
            }
        }
        
        serializer = PaymentStatisticsSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


# Active Gateways View
class ActiveGatewaysAPIView(views.APIView):
    """Get active payment gateways."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return active payment gateways."""
        gateways = PaymentGateway.objects.filter(is_active=True).order_by('sort_order', 'name')
        serializer = PaymentGatewayListSerializer(gateways, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
