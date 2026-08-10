"""
Discounts API Views
ViewSets and APIViews for discount models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.discounts.models import PriceRule, Coupon, Discount, CouponUsage
from api.serializers.discounts_serializers import (
    PriceRuleSerializer,
    PriceRuleListSerializer,
    CouponSerializer,
    CouponListSerializer,
    CouponCreateSerializer,
    CouponUpdateSerializer,
    CouponUsageSerializer,
    CouponUsageListSerializer,
    DiscountSerializer,
    DiscountListSerializer,
    CouponValidateSerializer,
    CouponValidationResultSerializer,
    DiscountCalculatorSerializer,
    DiscountStatsSerializer,
)
from api.pagination import CustomPageNumberPagination


class PriceRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for PriceRule model"""
    
    serializer_class = PriceRuleSerializer
    queryset = PriceRule.objects.filter(is_active=True).order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'discount_type', 'customer_selection', 'target_selection']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PriceRuleListSerializer
        return PriceRuleSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet for Coupon model"""
    
    serializer_class = CouponSerializer
    queryset = Coupon.objects.filter(is_active=True).order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'price_rule', 'per_customer_limit']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'created_at', 'starts_at', 'ends_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CouponListSerializer
        elif self.action == 'create':
            return CouponCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return CouponUpdateSerializer
        return CouponSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'validate']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        coupon = self.get_object()
        
        serializer = CouponValidateSerializer(data={
            'coupon_code': coupon.code,
            'user_id': request.user.id if request.user.is_authenticated else None
        })
        if serializer.is_valid():
            result = {
                'is_valid': coupon.is_valid(),
                'coupon': CouponListSerializer(coupon, context={'request': request}).data,
                'discount_amount': 0,
                'error': None
            }
            
            if not result['is_valid']:
                result['error'] = 'Coupon is not valid'
            
            serializer = CouponValidationResultSerializer(result)
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DiscountViewSet(viewsets.ModelViewSet):
    """ViewSet for Discount model"""
    
    serializer_class = DiscountSerializer
    queryset = Discount.objects.filter(is_active=True).order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'price_rule']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'starts_at', 'ends_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DiscountListSerializer
        return DiscountSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class CouponUsageViewSet(viewsets.ModelViewSet):
    """ViewSet for CouponUsage model"""
    
    serializer_class = CouponUsageSerializer
    queryset = CouponUsage.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['coupon', 'user', 'order']
    search_fields = ['coupon__code', 'user__email']
    ordering_fields = ['created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CouponUsageListSerializer
        return CouponUsageSerializer
    
    def get_permissions(self):
        return [IsAdminUser()]


class CouponValidateAPIView(APIView):
    """APIView for validating coupons"""
    
    permission_classes = [AllowAny]
    serializer_class = CouponValidateSerializer
    
    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        if serializer.is_valid():
            coupon_code = serializer.validated_data['coupon_code']
            cart_total = serializer.validated_data.get('cart_total')
            user_id = serializer.validated_data.get('user_id')
            product_ids = serializer.validated_data.get('product_ids', [])
            
            # Get coupon
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            except Coupon.DoesNotExist:
                return Response({
                    'is_valid': False,
                    'coupon': None,
                    'discount_amount': 0,
                    'error': 'Invalid coupon code'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validate coupon
            is_valid = coupon.is_valid()
            error = None
            discount_amount = 0
            
            if not is_valid:
                error = 'Coupon is not valid'
            elif coupon.minimum_order_value and cart_total < coupon.minimum_order_value:
                is_valid = False
                error = f'Minimum order value is {coupon.minimum_order_value}'
            elif user_id and coupon.per_customer_limit:
                usage_count = CouponUsage.objects.filter(coupon=coupon, user_id=user_id).count()
                if usage_count >= coupon.per_customer_limit:
                    is_valid = False
                    error = 'Coupon usage limit reached'
            else:
                # Calculate discount amount
                if coupon.price_rule.discount_type == 'percentage':
                    discount_amount = (cart_total * coupon.price_rule.value) / 100
                elif coupon.price_rule.discount_type == 'fixed_amount':
                    discount_amount = coupon.price_rule.value
                elif coupon.price_rule.discount_type == 'fixed_price':
                    discount_amount = cart_total - coupon.price_rule.value
                
                # Apply maximum discount amount
                if coupon.maximum_discount_amount and discount_amount > coupon.maximum_discount_amount:
                    discount_amount = coupon.maximum_discount_amount
            
            result = {
                'is_valid': is_valid,
                'coupon': CouponSerializer(coupon, context={'request': request}).data,
                'discount_amount': float(discount_amount),
                'error': error
            }
            
            serializer = CouponValidationResultSerializer(result)
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DiscountCalculatorAPIView(APIView):
    """APIView for calculating discounts"""
    
    permission_classes = [AllowAny]
    serializer_class = DiscountCalculatorSerializer
    
    def post(self, request):
        serializer = DiscountCalculatorSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data.get('product_id')
            variant_id = serializer.validated_data.get('variant_id')
            category_id = serializer.validated_data.get('category_id')
            brand_id = serializer.validated_data.get('brand_id')
            price = serializer.validated_data['price']
            quantity = serializer.validated_data.get('quantity', 1)
            user_id = serializer.validated_data.get('user_id')
            
            # Get applicable discounts
            discounts = Discount.objects.filter(
                is_active=True,
                starts_at__lte=self.request.date_today,
                ends_at__gte=self.request.date_today
            )
            
            # Filter by product
            if product_id:
                discounts = discounts.filter(
                    Q(applicable_products__id=product_id) | 
                    Q(applicable_products__isnull=True)
                )
            
            # Filter by category
            if category_id:
                discounts = discounts.filter(
                    Q(applicable_categories__id=category_id) | 
                    Q(applicable_categories__isnull=True)
                )
            
            # Filter by brand
            if brand_id:
                discounts = discounts.filter(
                    Q(applicable_brands__id=brand_id) | 
                    Q(applicable_brands__isnull=True)
                )
            
            # Calculate final price
            final_price = price * quantity
            discount_amount = 0
            applied_discounts = []
            
            for discount in discounts:
                if discount.price_rule.discount_type == 'percentage':
                    discount_amount = (final_price * discount.price_rule.value) / 100
                elif discount.price_rule.discount_type == 'fixed_amount':
                    discount_amount = discount.price_rule.value * quantity
                elif discount.price_rule.discount_type == 'fixed_price':
                    discount_amount = final_price - (discount.price_rule.value * quantity)
                
                applied_discounts.append({
                    'id': discount.id,
                    'name': discount.name,
                    'discount_type': discount.price_rule.discount_type,
                    'value': discount.price_rule.value,
                    'discount_amount': float(discount_amount)
                })
                final_price -= discount_amount
            
            return Response({
                'original_price': float(price * quantity),
                'final_price': float(final_price),
                'discount_amount': float(sum(d['discount_amount'] for d in applied_discounts)),
                'applied_discounts': applied_discounts
            })
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DiscountStatsAPIView(APIView):
    """APIView for discount statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count, Sum
        
        stats = {
            'total_coupons': Coupon.objects.count(),
            'active_coupons': Coupon.objects.filter(is_active=True).count(),
            'total_discounts': Discount.objects.count(),
            'active_discounts': Discount.objects.filter(is_active=True).count(),
            'total_usage': CouponUsage.objects.count(),
            'total_discount_amount': sum(float(u.discount_amount) for u in CouponUsage.objects.all()) or 0,
            'most_used_coupons': [],
            'recent_usage': []
        }
        
        # Most used coupons
        coupon_usage = CouponUsage.objects.values('coupon__id', 'coupon__code').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        for usage in coupon_usage:
            stats['most_used_coupons'].append({
                'id': usage['coupon__id'],
                'code': usage['coupon__code'],
                'usage_count': usage['count']
            })
        
        # Recent usage
        recent_usage = CouponUsage.objects.order_by('-created_at')[:10]
        for usage in recent_usage:
            stats['recent_usage'].append({
                'id': usage.id,
                'coupon_code': usage.coupon.code,
                'user_email': usage.user.email,
                'order_id': usage.order.id if usage.order else None,
                'discount_amount': float(usage.discount_amount),
                'created_at': usage.created_at
            })
        
        serializer = DiscountStatsSerializer(stats)
        return Response(serializer.data)
