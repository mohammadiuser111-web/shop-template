"""
Payments API Views
ViewSets and APIViews for payment models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.payments.models import (
    PaymentMethod, PaymentTransaction, Wallet, WalletTransaction, Refund
)
from apps.orders.models import Order
from api.serializers.payments_serializers import (
    PaymentMethodSerializer,
    PaymentMethodListSerializer,
    WalletSerializer,
    WalletTransactionSerializer,
    WalletTransactionListSerializer,
    RefundSerializer,
    RefundListSerializer,
    PaymentTransactionSerializer,
    PaymentTransactionListSerializer,
    PaymentTransactionCreateSerializer,
    PaymentVerifySerializer,
    PaymentCallbackSerializer,
    PaymentStatsSerializer,
    PaymentGatewayConfigSerializer,
)
from api.pagination import CustomPageNumberPagination


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for PaymentMethod model"""
    
    serializer_class = PaymentMethodSerializer
    queryset = PaymentMethod.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_test_mode']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentMethodListSerializer
        return PaymentMethodSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class WalletViewSet(viewsets.ModelViewSet):
    """ViewSet for Wallet model"""
    
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    def get_object(self):
        if self.request.user.is_staff:
            return super().get_object()
        return Wallet.objects.get(user=self.request.user)
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        if request.user.is_staff:
            user_id = request.query_params.get('user_id')
            if user_id:
                wallet = Wallet.objects.filter(user_id=user_id).first()
            else:
                wallet = Wallet.objects.filter(user=request.user).first()
        else:
            wallet = Wallet.objects.filter(user=request.user).first()
        
        if not wallet:
            return Response({'balance': 0, 'currency': 'USD'})
        
        return Response({
            'balance': float(wallet.balance),
            'currency': wallet.currency
        })


class WalletTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for WalletTransaction model"""
    
    serializer_class = WalletTransactionSerializer
    queryset = WalletTransaction.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['wallet', 'transaction_type']
    search_fields = ['description']
    ordering_fields = ['created_at', 'amount']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WalletTransactionListSerializer
        return WalletTransactionSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(wallet__user=self.request.user)


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for PaymentTransaction model"""
    
    serializer_class = PaymentTransactionSerializer
    queryset = PaymentTransaction.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['order', 'payment_method', 'status', 'user']
    search_fields = ['transaction_id', 'gateway_response']
    ordering_fields = ['created_at', 'amount', 'status']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentTransactionListSerializer
        return PaymentTransactionSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)


class RefundViewSet(viewsets.ModelViewSet):
    """ViewSet for Refund model"""
    
    serializer_class = RefundSerializer
    queryset = Refund.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['order', 'status']
    search_fields = ['refund_id', 'reason']
    ordering_fields = ['created_at', 'amount', 'status']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RefundListSerializer
        return RefundSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(order__user=self.request.user)


class PaymentVerifyAPIView(APIView):
    """APIView for verifying payment transactions"""
    
    permission_classes = [AllowAny]
    serializer_class = PaymentVerifySerializer
    
    def post(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        if serializer.is_valid():
            transaction_id = serializer.validated_data['transaction_id']
            gateway = serializer.validated_data['gateway']
            verification_data = serializer.validated_data['verification_data']
            
            # Get transaction
            try:
                transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
            except PaymentTransaction.DoesNotExist:
                return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # TODO: Verify payment with gateway
            # This will be implemented with actual payment gateway integration
            
            # Update transaction status
            transaction.status = 'completed'
            transaction.gateway_response = str(verification_data)
            transaction.save()
            
            # Update order status
            if transaction.order:
                transaction.order.payment_status = 'paid'
                transaction.order.status = 'processing'
                transaction.order.save()
            
            return Response({
                'status': 'success',
                'transaction_id': transaction.transaction_id,
                'status': transaction.status
            })
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCallbackAPIView(APIView):
    """APIView for payment gateway callbacks"""
    
    permission_classes = [AllowAny]
    serializer_class = PaymentCallbackSerializer
    
    def post(self, request):
        serializer = PaymentCallbackSerializer(data=request.data)
        if serializer.is_valid():
            transaction_id = serializer.validated_data['transaction_id']
            status = serializer.validated_data['status']
            gateway = serializer.validated_data['gateway']
            callback_data = serializer.validated_data['callback_data']
            
            # Get transaction
            try:
                transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
            except PaymentTransaction.DoesNotExist:
                return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Update transaction
            transaction.status = status
            transaction.gateway_response = str(callback_data)
            transaction.save()
            
            # Update order if exists
            if transaction.order:
                if status == 'completed':
                    transaction.order.payment_status = 'paid'
                    transaction.order.status = 'processing'
                elif status == 'failed':
                    transaction.order.payment_status = 'failed'
                    transaction.order.status = 'failed'
                transaction.order.save()
            
            return Response({'status': 'success', 'transaction_id': transaction.transaction_id})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatsAPIView(APIView):
    """APIView for payment statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count, Sum
        
        stats = {
            'total_transactions': PaymentTransaction.objects.count(),
            'successful_transactions': PaymentTransaction.objects.filter(status='completed').count(),
            'failed_transactions': PaymentTransaction.objects.filter(status='failed').count(),
            'total_amount': sum(float(t.amount) for t in PaymentTransaction.objects.filter(status='completed')) or 0,
            'payment_methods': {},
            'recent_transactions': [],
            'wallet_balance': 0
        }
        
        # Payment methods
        method_stats = PaymentTransaction.objects.values('payment_method__name').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        for method in method_stats:
            stats['payment_methods'][method['payment_method__name']] = {
                'count': method['count'],
                'total_amount': float(method['total_amount']) if method['total_amount'] else 0
            }
        
        # Recent transactions
        recent_transactions = PaymentTransaction.objects.filter(status='completed').order_by('-created_at')[:10]
        for transaction in recent_transactions:
            stats['recent_transactions'].append({
                'id': transaction.id,
                'transaction_id': transaction.transaction_id,
                'amount': float(transaction.amount),
                'currency': transaction.currency,
                'payment_method': transaction.payment_method.name if transaction.payment_method else 'Unknown',
                'created_at': transaction.created_at
            })
        
        # Wallet balance
        if request.user.is_authenticated:
            wallet = Wallet.objects.filter(user=request.user).first()
            if wallet:
                stats['wallet_balance'] = float(wallet.balance)
        
        serializer = PaymentStatsSerializer(stats)
        return Response(serializer.data)


class PaymentGatewayConfigAPIView(APIView):
    """APIView for payment gateway configuration"""
    
    permission_classes = [IsAdminUser]
    serializer_class = PaymentGatewayConfigSerializer
    
    def get(self, request):
        # Get all payment methods with their configurations
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        
        configs = []
        for method in payment_methods:
            configs.append({
                'gateway': method.code,
                'is_enabled': method.is_active,
                'config': {
                    'name': method.name,
                    'description': method.description,
                    'logo': method.logo.url if method.logo else None
                }
            })
        
        return Response({'gateways': configs})
    
    def post(self, request):
        serializer = PaymentGatewayConfigSerializer(data=request.data)
        if serializer.is_valid():
            gateway = serializer.validated_data['gateway']
            is_enabled = serializer.validated_data['is_enabled']
            config = serializer.validated_data['config']
            
            # Update payment method
            try:
                method = PaymentMethod.objects.get(code=gateway)
                method.is_active = is_enabled
                method.save()
                
                # TODO: Update gateway specific configuration
                
                return Response({'status': 'success', 'gateway': gateway})
            except PaymentMethod.DoesNotExist:
                return Response({'error': 'Gateway not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
