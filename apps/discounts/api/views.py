"""
API views for Discounts app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import uuid

from ..models import Discount, Coupon, Campaign, CouponUsage
from apps.orders.models import Order
from apps.accounts.models import User
from .serializers import (
    DiscountSerializer, DiscountListSerializer,
    CouponSerializer, CouponListSerializer,
    CouponCreateSerializer, CouponValidateSerializer,
    CouponValidateResponseSerializer, CampaignSerializer,
    CampaignListSerializer, CampaignCreateSerializer,
    CouponUsageSerializer, CouponUsageListSerializer,
    DiscountStatisticsSerializer
)


# Discount Views
class DiscountListAPIView(generics.ListAPIView):
    """List discounts."""
    
    serializer_class = DiscountListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Discount.objects.all().order_by('-created_at')


class DiscountRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve discount."""
    
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Discount.objects.all()


# Coupon Views
class CouponListAPIView(generics.ListAPIView):
    """List coupons."""
    
    serializer_class = CouponListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get coupons."""
        if self.request.user.is_superuser:
            return Coupon.objects.all().order_by('-created_at')
        
        # For regular users, only return public coupons that are active
        return Coupon.objects.filter(
            coupon_type='public',
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).order_by('-created_at')


class CouponRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve coupon."""
    
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Coupon.objects.all()


class CouponCreateAPIView(generics.CreateAPIView):
    """Create coupon."""
    
    serializer_class = CouponCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class CouponUpdateAPIView(generics.UpdateAPIView):
    """Update coupon."""
    
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Coupon.objects.all()


class CouponDestroyAPIView(generics.DestroyAPIView):
    """Delete coupon."""
    
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Coupon.objects.all()


class CouponValidateAPIView(views.APIView):
    """Validate a coupon code."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Validate coupon."""
        serializer = CouponValidateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        code = serializer.validated_data['code']
        order_id = serializer.validated_data.get('order_id')
        user_id = serializer.validated_data.get('user_id')
        order_total = serializer.validated_data.get('order_total', 0)
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({
                'is_valid': False,
                'message': 'Coupon not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if coupon is valid
        if not coupon.is_valid():
            return Response({
                'is_valid': False,
                'message': 'Coupon is not active or has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check user restrictions
        user = None
        if user_id:
            user = get_object_or_404(User, pk=user_id)
        else:
            user = request.user
        
        if coupon.coupon_type == 'user' and user not in coupon.allowed_users.all():
            return Response({
                'is_valid': False,
                'message': 'Coupon is restricted to specific users'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if coupon.coupon_type == 'email':
            allowed_emails = [e.strip() for e in coupon.allowed_emails.split(',') if e.strip()]
            if user.email not in allowed_emails:
                return Response({
                    'is_valid': False,
                    'message': 'Coupon is restricted to specific email addresses'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Check order amount
        if coupon.min_order_amount and order_total < coupon.min_order_amount:
            return Response({
                'is_valid': False,
                'message': f'Minimum order amount: {coupon.min_order_amount}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if coupon.max_order_amount and order_total > coupon.max_order_amount:
            return Response({
                'is_valid': False,
                'message': f'Maximum order amount: {coupon.max_order_amount}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check max uses
        if coupon.max_uses and coupon.get_usage_count() >= coupon.max_uses:
            return Response({
                'is_valid': False,
                'message': 'Coupon has reached maximum usage limit'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check user usage limit
        if coupon.max_uses_per_user:
            user_uses = coupon.get_user_usage_count(user)
            if user_uses >= coupon.max_uses_per_user:
                return Response({
                    'is_valid': False,
                    'message': f'You have reached the maximum usage limit ({coupon.max_uses_per_user}) for this coupon'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount amount
        discount_amount = coupon.calculate_discount(order_total)
        
        data = {
            'is_valid': True,
            'coupon_id': coupon.id,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'discount_amount': discount_amount,
            'message': 'Coupon is valid',
            'free_shipping': coupon.free_shipping
        }
        
        serializer = CouponValidateResponseSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


class CouponApplyAPIView(views.APIView):
    """Apply a coupon to an order."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """Apply coupon to order."""
        serializer = CouponValidateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        code = serializer.validated_data['code']
        order_id = serializer.validated_data.get('order_id')
        
        if not order_id:
            return Response({'detail': 'Order ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({'detail': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)
        
        order = get_object_or_404(Order, pk=order_id)
        
        # Check if user can apply this coupon to this order
        if order.user != request.user and not request.user.is_superuser:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Validate coupon
        if not coupon.is_valid_for_order(order):
            return Response({'detail': 'Coupon is not valid for this order'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Apply coupon to order
        order.coupon = coupon
        order.discount = coupon.calculate_discount(order.subtotal)
        order.calculate_totals()
        order.save()
        
        # Record usage
        CouponUsage.objects.create(
            coupon=coupon,
            order=order,
            user=request.user,
            discount_amount=coupon.calculate_discount(order.subtotal)
        )
        
        # Increment usage count
        coupon.uses_count += 1
        coupon.save()
        
        return Response({
            'detail': 'Coupon applied successfully',
            'coupon_id': coupon.id,
            'discount_amount': order.discount,
            'total_amount': order.total_amount
        }, status=status.HTTP_200_OK)


# Campaign Views
class CampaignListAPIView(generics.ListAPIView):
    """List campaigns."""
    
    serializer_class = CampaignListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get campaigns."""
        if self.request.user.is_superuser:
            return Campaign.objects.all().order_by('-priority', '-created_at')
        
        # For regular users, only return active campaigns
        return Campaign.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).order_by('-priority', '-created_at')


class CampaignRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve campaign."""
    
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Campaign.objects.all()


class CampaignCreateAPIView(generics.CreateAPIView):
    """Create campaign."""
    
    serializer_class = CampaignCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class CampaignUpdateAPIView(generics.UpdateAPIView):
    """Update campaign."""
    
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Campaign.objects.all()


class CampaignDestroyAPIView(generics.DestroyAPIView):
    """Delete campaign."""
    
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Campaign.objects.all()


# Coupon Usage Views
class CouponUsageListAPIView(generics.ListAPIView):
    """List coupon usages."""
    
    serializer_class = CouponUsageListSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Get coupon usages."""
        coupon_id = self.kwargs.get('coupon_id')
        
        if coupon_id:
            coupon = get_object_or_404(Coupon, pk=coupon_id)
            return CouponUsage.objects.filter(coupon=coupon)
        
        return CouponUsage.objects.all()


class CouponUsageRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve coupon usage."""
    
    serializer_class = CouponUsageSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = CouponUsage.objects.all()


# Discount Statistics View
class DiscountStatisticsAPIView(views.APIView):
    """Get discount statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Return discount statistics."""
        from django.db.models import Count, Sum
        
        # Total coupons
        total_coupons = Coupon.objects.count()
        
        # Total campaigns
        total_campaigns = Campaign.objects.count()
        
        # Active coupons
        active_coupons = Coupon.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).count()
        
        # Active campaigns
        active_campaigns = Campaign.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).count()
        
        # Total usage
        total_usage = CouponUsage.objects.count()
        
        # Total discount amount
        total_discount_amount = CouponUsage.objects.aggregate(
            total=Sum('discount_amount')
        )['total'] or 0
        
        data = {
            'total_coupons': total_coupons,
            'total_campaigns': total_campaigns,
            'active_coupons': active_coupons,
            'active_campaigns': active_campaigns,
            'total_usage': total_usage,
            'total_discount_amount': total_discount_amount
        }
        
        serializer = DiscountStatisticsSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


# Available Coupons View
class AvailableCouponsAPIView(views.APIView):
    """Get available coupons for checkout."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Return available coupons."""
        # Get public coupons that are active and valid
        coupons = Coupon.objects.filter(
            coupon_type='public',
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).order_by('-created_at')
        
        # For authenticated users, also include user-specific coupons
        if request.user.is_authenticated:
            user_coupons = Coupon.objects.filter(
                coupon_type='user',
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
                allowed_users=request.user
            )
            coupons = coupons.union(user_coupons)
            
            # Also check email-restricted coupons
            email_coupons = Coupon.objects.filter(
                coupon_type='email',
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )
            for coupon in email_coupons:
                allowed_emails = [e.strip() for e in coupon.allowed_emails.split(',') if e.strip()]
                if request.user.email in allowed_emails:
                    coupons = coupons.union(Coupon.objects.filter(pk=coupon.pk))
        
        serializer = CouponListSerializer(coupons.distinct(), many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Active Campaigns View
class ActiveCampaignsAPIView(views.APIView):
    """Get active campaigns."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return active campaigns."""
        campaigns = Campaign.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).order_by('-priority', '-created_at')
        
        serializer = CampaignListSerializer(campaigns, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
