"""
API views for Orders app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from ..models import Order, OrderItem, Refund
from apps.accounts.models import UserAddress
from apps.products.models import Product, ProductVariant
from apps.discounts.models import Coupon
from apps.shipping.models import ShippingMethod
from .serializers import (
    OrderSerializer, OrderDetailSerializer, OrderItemSerializer,
    RefundSerializer,
    OrderCreateSerializer, OrderUpdateSerializer,
    OrderCancelSerializer, OrderStatusSerializer
)


# Order Views
class OrderListAPIView(generics.ListAPIView):
    """List orders."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's orders."""
        if self.request.user.is_superuser:
            # Admin can see all orders
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve order details."""
    
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'
    
    def get_queryset(self):
        """Get orders."""
        if self.request.user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


class OrderCreateAPIView(views.APIView):
    """Create a new order."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """Create order from cart."""
        serializer = OrderCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Get shipping address
        shipping_address = get_object_or_404(UserAddress, pk=serializer.validated_data['shipping_address_id'], user=user)
        
        # Get billing address
        billing_address = None
        if serializer.validated_data.get('billing_address_id'):
            billing_address = get_object_or_404(UserAddress, pk=serializer.validated_data['billing_address_id'], user=user)
        
        # Get cart
        from apps.cart.models import Cart
        cart = Cart.objects.filter(user=user, is_active=True).first()
        
        if not cart or cart.items.count() == 0:
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create order
        order = Order.objects.create(
            user=user,
            status='pending',
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=serializer.validated_data['payment_method'],
            shipping_method=serializer.validated_data['shipping_method'],
            notes=serializer.validated_data.get('notes', ''),
            currency='IRR'
        )
        
        # Add items from cart
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=cart_item.price
            )
        
        # Apply coupon if specified
        coupon_code = serializer.validated_data.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                # Check if coupon is valid for this user and order
                if coupon.is_valid():
                    order.coupon = coupon
                    order.discount = coupon.get_discount_amount(order.subtotal)
            except Coupon.DoesNotExist:
                pass
        
        # Calculate totals
        order.calculate_totals()
        order.save()
        
        # Deactivate cart
        cart.is_active = False
        cart.save()
        
        serializer = OrderDetailSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderUpdateAPIView(generics.UpdateAPIView):
    """Update order."""
    
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'order_number'


class OrderCancelAPIView(views.APIView):
    """Cancel an order."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, order_number):
        """Cancel order."""
        order = get_object_or_404(Order, order_number=order_number)
        
        # Check if user can cancel this order
        if not request.user.is_superuser and order.user != request.user:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if order can be cancelled
        if order.status not in ['pending', 'processing']:
            return Response({'detail': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = OrderCancelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Cancel order
        order.status = 'cancelled'
        order.cancelled_reason = serializer.validated_data['reason']
        order.save()
        
        # Restore cart items
        from apps.cart.models import Cart, CartItem
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'is_active': True}
        )
        
        for item in order.items.all():
            CartItem.objects.create(
                cart=cart,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                price=item.price
            )
        
        serializer = OrderDetailSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderStatusUpdateAPIView(views.APIView):
    """Update order status."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, order_number):
        """Update order status."""
        order = get_object_or_404(Order, order_number=order_number)
        
        serializer = OrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')
        
        # Update status
        order.status = new_status
        order.save()
        
        serializer = OrderDetailSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Order Item Views
class OrderItemListAPIView(generics.ListAPIView):
    """List order items."""
    
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get order items."""
        order_number = self.kwargs.get('order_number')
        order = get_object_or_404(Order, order_number=order_number)
        
        if not self.request.user.is_superuser and order.user != self.request.user:
            return OrderItem.objects.none()
        
        return OrderItem.objects.filter(order=order)


class OrderItemRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve order item."""
    
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get order items."""
        if self.request.user.is_superuser:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__user=self.request.user)


# Refund Views
class RefundListCreateAPIView(generics.ListCreateAPIView):
    """List and create refunds."""
    
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get refunds."""
        if self.request.user.is_superuser:
            return Refund.objects.all()
        return Refund.objects.filter(order__user=self.request.user)
    
    def perform_create(self, serializer):
        """Create refund."""
        order_number = self.kwargs.get('order_number')
        order = get_object_or_404(Order, order_number=order_number)
        
        if not self.request.user.is_superuser and order.user != self.request.user:
            raise permissions.PermissionDenied('Permission denied')
        
        serializer.save(
            order=order,
            processed_by=self.request.user if self.request.user.is_superuser else None,
            processed_at=timezone.now() if self.request.user.is_superuser else None
        )


class RefundRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve refund."""
    
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get refunds."""
        if self.request.user.is_superuser:
            return Refund.objects.all()
        return Refund.objects.filter(order__user=self.request.user)


# User Orders Views
class UserOrdersAPIView(generics.ListAPIView):
    """List user's orders."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's orders."""
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class UserOrderRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve user's order."""
    
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'
    
    def get_queryset(self):
        """Get user's orders."""
        return Order.objects.filter(user=self.request.user)


# Recent Orders View
class RecentOrdersAPIView(views.APIView):
    """Get recent orders."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Return recent orders."""
        limit = int(request.query_params.get('limit', 5))
        
        if request.user.is_superuser:
            orders = Order.objects.all().order_by('-created_at')[:limit]
        else:
            orders = Order.objects.filter(user=request.user).order_by('-created_at')[:limit]
        
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Order Statistics View
class OrderStatisticsAPIView(views.APIView):
    """Get order statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Return order statistics."""
        from django.db.models import Count, Sum, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        # Today
        today = timezone.now().date()
        today_orders = Order.objects.filter(created_at__date=today)
        
        # This week
        week_start = today - timedelta(days=today.weekday())
        week_orders = Order.objects.filter(created_at__date__gte=week_start)
        
        # This month
        month_start = today.replace(day=1)
        month_orders = Order.objects.filter(created_at__date__gte=month_start)
        
        # All time
        all_orders = Order.objects.all()
        
        data = {
            'today': {
                'count': today_orders.count(),
                'total': today_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
                'average': today_orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
            },
            'this_week': {
                'count': week_orders.count(),
                'total': week_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
                'average': week_orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
            },
            'this_month': {
                'count': month_orders.count(),
                'total': month_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
                'average': month_orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
            },
            'all_time': {
                'count': all_orders.count(),
                'total': all_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
                'average': all_orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
            },
            'status_distribution': {
                'pending': Order.objects.filter(status='pending').count(),
                'processing': Order.objects.filter(status='processing').count(),
                'shipped': Order.objects.filter(status='shipped').count(),
                'delivered': Order.objects.filter(status='delivered').count(),
                'cancelled': Order.objects.filter(status='cancelled').count(),
                'refunded': Order.objects.filter(status='refunded').count()
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
