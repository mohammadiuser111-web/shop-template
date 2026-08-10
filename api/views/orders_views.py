"""
Orders API Views
ViewSets and APIViews for order models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.orders.models import Order, OrderItem, Shipping, OrderStatus
from apps.cart.models import Cart
from apps.accounts.models import UserAddress
from apps.shipping.models import ShippingMethod
from apps.discounts.models import Coupon
from api.serializers.orders_serializers import (
    OrderItemSerializer,
    OrderItemListSerializer,
    ShippingSerializer,
    ShippingListSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    OrderStatusUpdateSerializer,
    OrderCancelSerializer,
    OrderRefundSerializer,
    OrderStatsSerializer,
    OrderExportSerializer,
)
from api.pagination import CustomPageNumberPagination


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order model"""
    
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'status', 'payment_status']
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'updated_at', 'total', 'status']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        order = self.get_object()
        items = OrderItem.objects.filter(order=order)
        serializer = OrderItemListSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def shipping(self, request, pk=None):
        order = self.get_object()
        if order.shipping:
            serializer = ShippingSerializer(order.shipping, context={'request': request})
            return Response(serializer.data)
        return Response({'error': 'No shipping information'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['pending', 'processing']:
            return Response({'error': 'Order cannot be cancelled in current status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'cancelled'
        order.save()
        
        # Add status history
        OrderStatus.objects.create(
            order=order,
            status='cancelled',
            notes='Order cancelled by customer'
        )
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet for OrderItem model"""
    
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['order', 'product', 'variant']
    search_fields = ['product__name', 'variant__name']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderItemListSerializer
        return OrderItemSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(order__user=self.request.user)


class ShippingViewSet(viewsets.ModelViewSet):
    """ViewSet for Shipping model"""
    
    serializer_class = ShippingSerializer
    queryset = Shipping.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['order', 'shipping_method']
    search_fields = ['tracking_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ShippingListSerializer
        return ShippingSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(order__user=self.request.user)


class OrderCreateAPIView(APIView):
    """APIView for creating orders from cart"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer
    
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            cart_id = serializer.validated_data['cart_id']
            shipping_method_id = serializer.validated_data['shipping_method_id']
            shipping_address_id = serializer.validated_data['shipping_address_id']
            coupon_code = serializer.validated_data.get('coupon_code', '')
            notes = serializer.validated_data.get('notes', '')
            
            # Get cart
            try:
                cart = Cart.objects.get(cart_id=cart_id, user=request.user)
            except Cart.DoesNotExist:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if cart.items.count() == 0:
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get shipping method
            try:
                shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
            except ShippingMethod.DoesNotExist:
                return Response({'error': 'Shipping method not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get shipping address
            try:
                shipping_address = UserAddress.objects.get(id=shipping_address_id, user=request.user)
            except UserAddress.DoesNotExist:
                return Response({'error': 'Shipping address not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get coupon if provided
            coupon = None
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                    if not coupon.is_valid():
                        return Response({'error': 'Coupon is not valid'}, status=status.HTTP_400_BAD_REQUEST)
                except Coupon.DoesNotExist:
                    return Response({'error': 'Invalid coupon code'}, status=status.HTTP_404_NOT_FOUND)
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                order_number=Order.generate_order_number(),
                subtotal=cart.subtotal,
                discount_amount=cart.discount_amount,
                shipping_cost=shipping_method.get_cost(cart),
                tax_amount=0,  # Will be calculated based on settings
                total=cart.total + shipping_method.get_cost(cart),
                notes=notes,
                status='pending',
                payment_status='pending'
            )
            
            # Create shipping
            Shipping.objects.create(
                order=order,
                shipping_method=shipping_method,
                shipping_address=shipping_address,
                cost=shipping_method.get_cost(cart)
            )
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    final_price=cart_item.final_price
                )
            
            # Apply coupon
            if coupon:
                order.coupon = coupon
                order.save()
            
            # Clear cart
            cart.items.all().delete()
            cart.coupon = None
            cart.save()
            
            serializer = OrderSerializer(order, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OrderUpdateAPIView(APIView):
    """APIView for updating orders"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = OrderUpdateSerializer
    
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OrderStatusUpdateAPIView(APIView):
    """APIView for updating order status"""
    
    permission_classes = [IsAdminUser]
    serializer_class = OrderStatusUpdateSerializer
    
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            status = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')
            notify_customer = serializer.validated_data.get('notify_customer', True)
            
            old_status = order.status
            order.status = status
            order.save()
            
            # Add status history
            OrderStatus.objects.create(
                order=order,
                status=status,
                notes=notes or f'Status changed from {old_status} to {status}'
            )
            
            # TODO: Send notification if notify_customer is True
            
            return Response({'status': 'success', 'order_id': order.id})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OrderCancelAPIView(APIView):
    """APIView for cancelling orders"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCancelSerializer
    
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if order.status not in ['pending', 'processing']:
            return Response({'error': 'Order cannot be cancelled in current status'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = OrderCancelSerializer(data=request.data)
        if serializer.is_valid():
            reason = serializer.validated_data['reason']
            refund_requested = serializer.validated_data.get('refund_requested', False)
            
            order.status = 'cancelled'
            order.save()
            
            # Add status history
            OrderStatus.objects.create(
                order=order,
                status='cancelled',
                notes=f'Order cancelled by customer. Reason: {reason}'
            )
            
            # TODO: Handle refund request if needed
            
            return Response({'status': 'success', 'order_id': order.id})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OrderRefundAPIView(APIView):
    """APIView for requesting order refunds"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = OrderRefundSerializer
    
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderRefundSerializer(data=request.data)
        if serializer.is_valid():
            items = serializer.validated_data.get('items', [])
            reason = serializer.validated_data['reason']
            amount = serializer.validated_data.get('amount')
            
            # TODO: Create refund request
            # This will be handled by the refund system
            
            return Response({'status': 'success', 'message': 'Refund request submitted'})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OrderStatsAPIView(APIView):
    """APIView for order statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count, Sum, Avg
        from datetime import timedelta
        
        stats = {
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'processing_orders': Order.objects.filter(status='processing').count(),
            'shipped_orders': Order.objects.filter(status='shipped').count(),
            'delivered_orders': Order.objects.filter(status='delivered').count(),
            'cancelled_orders': Order.objects.filter(status='cancelled').count(),
            'total_revenue': sum(float(o.total) for o in Order.objects.filter(status='delivered')) or 0,
            'average_order_value': 0,
            'orders_by_date': {},
            'orders_by_status': {},
            'recent_orders': [],
            'top_products': [],
        }
        
        # Calculate average order value
        delivered_orders = Order.objects.filter(status='delivered')
        if delivered_orders.exists():
            stats['average_order_value'] = sum(float(o.total) for o in delivered_orders) / delivered_orders.count()
        
        # Orders by date (last 30 days)
        thirty_days_ago = self.request.date_today - timedelta(days=30)
        daily_orders = Order.objects.filter(created_at__gte=thirty_days_ago).values('created_at__date').annotate(
            count=Count('id')
        )
        for day in daily_orders:
            stats['orders_by_date'][str(day['created_at__date'])] = day['count']
        
        # Orders by status
        status_counts = Order.objects.values('status').annotate(count=Count('id'))
        for status_count in status_counts:
            stats['orders_by_status'][status_count['status']] = status_count['count']
        
        # Recent orders
        recent_orders = Order.objects.order_by('-created_at')[:10]
        for order in recent_orders:
            stats['recent_orders'].append({
                'id': order.id,
                'order_number': order.order_number,
                'user_email': order.user.email,
                'total': float(order.total),
                'status': order.status,
                'created_at': order.created_at
            })
        
        # Top products
        from apps.orders.models import OrderItem
        top_products = OrderItem.objects.values('product__id', 'product__name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')[:10]
        
        for product in top_products:
            stats['top_products'].append({
                'id': product['product__id'],
                'name': product['product__name'],
                'total_sold': product['total_quantity']
            })
        
        serializer = OrderStatsSerializer(stats)
        return Response(serializer.data)


class OrderExportAPIView(APIView):
    """APIView for exporting orders"""
    
    permission_classes = [IsAdminUser]
    serializer_class = OrderExportSerializer
    
    def get(self, request):
        serializer = OrderExportSerializer(data=request.query_params)
        if serializer.is_valid():
            format_type = serializer.validated_data.get('format', 'csv')
            date_from = serializer.validated_data.get('date_from')
            date_to = serializer.validated_data.get('date_to')
            status = serializer.validated_data.get('status')
            payment_status = serializer.validated_data.get('payment_status')
            user_id = serializer.validated_data.get('user_id')
            
            # Filter orders
            queryset = Order.objects.all()
            
            if date_from:
                queryset = queryset.filter(created_at__gte=date_from)
            if date_to:
                queryset = queryset.filter(created_at__lte=date_to)
            if status:
                queryset = queryset.filter(status=status)
            if payment_status:
                queryset = queryset.filter(payment_status=payment_status)
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            
            # TODO: Generate export file based on format
            # This will be implemented with proper file generation
            
            return Response({
                'status': 'success',
                'message': f'Export will be generated in {format_type} format',
                'count': queryset.count()
            })
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
