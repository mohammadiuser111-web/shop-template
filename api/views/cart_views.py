"""
Cart API Views
ViewSets and APIViews for cart models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from apps.cart.models import Cart, CartItem
from apps.products.models import Product, ProductVariant
from apps.discounts.models import Coupon
from api.serializers.cart_serializers import (
    CartItemSerializer,
    CartItemListSerializer,
    CartSerializer,
    CartListSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    RemoveFromCartSerializer,
    ClearCartSerializer,
    ApplyCouponSerializer,
    RemoveCouponSerializer,
    CartSummarySerializer,
)
from api.pagination import CustomPageNumberPagination


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for Cart model"""
    
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CartListSerializer
        return CartSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return self.queryset.filter(session_key=self.request.session.session_key)
    
    def get_object(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart
    
    def get_permissions(self):
        return [AllowAny()]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        cart = self.get_object()
        serializer = CartSummarySerializer(cart, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_object()
        cart.items.all().delete()
        cart.coupon = None
        cart.save()
        return Response({'status': 'success'})


class CartItemViewSet(viewsets.ModelViewSet):
    """ViewSet for CartItem model"""
    
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CartItemListSerializer
        return CartItemSerializer
    
    def get_queryset(self):
        cart = Cart.objects.filter(user=self.request.user).first()
        if cart:
            return self.queryset.filter(cart=cart)
        return self.queryset.none()
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        cart = Cart.objects.get_or_create(user=self.request.user)[0]
        serializer.save(cart=cart)


class AddToCartAPIView(APIView):
    """APIView for adding items to cart"""
    
    permission_classes = [AllowAny]
    serializer_class = AddToCartSerializer
    
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            variant_id = serializer.validated_data.get('variant_id')
            quantity = serializer.validated_data['quantity']
            
            # Get product
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get variant if provided
            variant = None
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product)
                except ProductVariant.DoesNotExist:
                    return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get or create cart
            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                cart, created = Cart.objects.get_or_create(session_key=session_key)
            
            # Check if item already exists
            if variant:
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    variant=variant,
                    defaults={'quantity': quantity}
                )
            else:
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            # Update cart totals
            cart.update_totals()
            
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UpdateCartItemAPIView(APIView):
    """APIView for updating cart item quantity"""
    
    permission_classes = [AllowAny]
    serializer_class = UpdateCartItemSerializer
    
    def post(self, request):
        serializer = UpdateCartItemSerializer(data=request.data)
        if serializer.is_valid():
            item_id = serializer.validated_data['item_id']
            quantity = serializer.validated_data['quantity']
            
            try:
                cart_item = CartItem.objects.get(id=item_id)
            except CartItem.DoesNotExist:
                return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
            
            cart_item.quantity = quantity
            cart_item.save()
            
            # Update cart totals
            cart_item.cart.update_totals()
            
            serializer = CartSerializer(cart_item.cart, context={'request': request})
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RemoveFromCartAPIView(APIView):
    """APIView for removing items from cart"""
    
    permission_classes = [AllowAny]
    serializer_class = RemoveFromCartSerializer
    
    def post(self, request):
        serializer = RemoveFromCartSerializer(data=request.data)
        if serializer.is_valid():
            item_id = serializer.validated_data['item_id']
            
            try:
                cart_item = CartItem.objects.get(id=item_id)
                cart = cart_item.cart
                cart_item.delete()
                
                # Update cart totals
                cart.update_totals()
                
                serializer = CartSerializer(cart, context={'request': request})
                return Response(serializer.data)
            except CartItem.DoesNotExist:
                return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ClearCartAPIView(APIView):
    """APIView for clearing cart"""
    
    permission_classes = [AllowAny]
    serializer_class = ClearCartSerializer
    
    def post(self, request):
        serializer = ClearCartSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.is_authenticated:
                cart = Cart.objects.filter(user=request.user).first()
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                cart = Cart.objects.filter(session_key=session_key).first()
            
            if cart:
                cart.items.all().delete()
                cart.coupon = None
                cart.save()
            
            return Response({'status': 'success'})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ApplyCouponAPIView(APIView):
    """APIView for applying coupon to cart"""
    
    permission_classes = [AllowAny]
    serializer_class = ApplyCouponSerializer
    
    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        if serializer.is_valid():
            coupon_code = serializer.validated_data['coupon_code']
            
            # Get cart
            if request.user.is_authenticated:
                cart = Cart.objects.filter(user=request.user).first()
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                cart = Cart.objects.filter(session_key=session_key).first()
            
            if not cart:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get coupon
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            except Coupon.DoesNotExist:
                return Response({'error': 'Invalid coupon code'}, status=status.HTTP_404_NOT_FOUND)
            
            # Validate coupon
            if not coupon.is_valid():
                return Response({'error': 'Coupon is not valid'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if coupon can be applied to this cart
            if not coupon.is_applicable_to_cart(cart):
                return Response({'error': 'Coupon cannot be applied to this cart'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Apply coupon
            cart.coupon = coupon
            cart.update_totals()
            cart.save()
            
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RemoveCouponAPIView(APIView):
    """APIView for removing coupon from cart"""
    
    permission_classes = [AllowAny]
    serializer_class = RemoveCouponSerializer
    
    def post(self, request):
        serializer = RemoveCouponSerializer(data=request.data)
        if serializer.is_valid():
            # Get cart
            if request.user.is_authenticated:
                cart = Cart.objects.filter(user=request.user).first()
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                cart = Cart.objects.filter(session_key=session_key).first()
            
            if not cart:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Remove coupon
            cart.coupon = None
            cart.update_totals()
            cart.save()
            
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CartSummaryAPIView(APIView):
    """APIView for cart summary"""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Get cart
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first()
        
        if not cart:
            return Response({
                'cart_id': None,
                'item_count': 0,
                'items': [],
                'subtotal': 0,
                'discount_amount': 0,
                'discount_code': None,
                'total': 0,
                'shipping_cost': None,
                'grand_total': 0
            })
        
        serializer = CartSummarySerializer(cart, context={'request': request})
        return Response(serializer.data)
