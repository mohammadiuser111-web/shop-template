"""
API views for Cart app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import Cart, CartItem
from apps.products.models import Product, ProductVariant
from apps.discounts.models import Coupon
from .serializers import (
    CartSerializer, CartItemSerializer,
    AddToCartSerializer, UpdateCartItemSerializer,
    ApplyCouponSerializer
)


class CartRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve user cart."""
    
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create cart for user."""
        user = self.request.user
        cart, created = Cart.objects.get_or_create(
            user=user,
            defaults={'is_active': True}
        )
        
        # If cart exists but is not active, reactivate it
        if not created and not cart.is_active:
            cart.is_active = True
            cart.save()
        
        return cart


class CartCreateAPIView(views.APIView):
    """Create a new cart."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Create cart."""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                defaults={'is_active': True}
            )
            if not created and not cart.is_active:
                cart.is_active = True
                cart.save()
        else:
            # Create session-based cart
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                defaults={'is_active': True}
            )
        
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddToCartAPIView(views.APIView):
    """Add item to cart."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Add item to cart."""
        serializer = AddToCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        variant_id = serializer.validated_data.get('variant_id')
        
        # Get product
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        
        # Get variant if specified
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, pk=variant_id, product=product)
        
        # Get cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                defaults={'is_active': True}
            )
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                defaults={'is_active': True}
            )
        
        # Check if item already exists in cart
        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # Create new cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity,
                price=variant.price if variant else product.price
            )
        
        # Recalculate cart
        cart.calculate_totals()
        
        serializer = CartItemSerializer(cart_item, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemListAPIView(generics.ListAPIView):
    """List cart items."""
    
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get cart items."""
        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
        else:
            session_key = self.request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
            else:
                cart = None
        
        if cart:
            return CartItem.objects.filter(cart=cart).select_related('product', 'variant')
        return CartItem.objects.none()


class CartItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete cart item."""
    
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get cart items for current cart."""
        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
        else:
            session_key = self.request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
            else:
                cart = None
        
        if cart:
            return CartItem.objects.filter(cart=cart)
        return CartItem.objects.none()
    
    def perform_update(self, serializer):
        """Update cart item and recalculate cart."""
        cart_item = serializer.save()
        cart_item.cart.calculate_totals()


class UpdateCartItemAPIView(views.APIView):
    """Update cart item quantity."""
    
    permission_classes = [permissions.AllowAny]
    
    def patch(self, request, pk):
        """Update cart item quantity."""
        # Get cart
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
            else:
                cart = None
        
        if not cart:
            return Response({'detail': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get cart item
        cart_item = get_object_or_404(CartItem, pk=pk, cart=cart)
        
        # Update quantity
        serializer = UpdateCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()
        
        # Recalculate cart
        cart.calculate_totals()
        
        serializer = CartItemSerializer(cart_item, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveFromCartAPIView(views.APIView):
    """Remove item from cart."""
    
    permission_classes = [permissions.AllowAny]
    
    def delete(self, request, pk):
        """Remove item from cart."""
        # Get cart
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
            else:
                cart = None
        
        if not cart:
            return Response({'detail': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get and delete cart item
        cart_item = get_object_or_404(CartItem, pk=pk, cart=cart)
        cart_item.delete()
        
        # Recalculate cart
        cart.calculate_totals()
        
        return Response({'detail': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)


class ClearCartAPIView(views.APIView):
    """Clear all items from cart."""
    
    permission_classes = [permissions.AllowAny]
    
    def delete(self, request):
        """Clear cart."""
        # Get cart
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
            else:
                cart = None
        
        if not cart:
            return Response({'detail': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Delete all items
        cart.items.all().delete()
        
        # Recalculate cart
        cart.calculate_totals()
        
        return Response({'detail': 'Cart cleared'}, status=status.HTTP_204_NO_CONTENT)


class CartTotalsAPIView(views.APIView):
    """Get cart totals."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return cart totals."""
        # Get cart
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
            else:
                cart = None
        
        if not cart:
            return Response({
                'item_count': 0,
                'subtotal': 0,
                'total': 0,
                'discount': 0,
                'tax': 0,
                'grand_total': 0
            }, status=status.HTTP_200_OK)
        
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
