"""
Views for cart app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
import uuid

from .models import Cart, CartItem
from .forms import (
    AddToCartForm, UpdateCartItemForm, RemoveFromCartForm,
    ClearCartForm, ApplyCouponForm, RemoveCouponForm
)
from apps.products.models import Product, ProductVariant
from apps.discounts.models import Coupon


def get_or_create_cart(request):
    """Get or create cart for the current user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            cart_type='user',
            defaults={'session_key': ''}
        )
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            cart_type='session',
            defaults={'user': None}
        )
    
    return cart


@require_http_methods(["GET"])
def view_cart(request):
    """View shopping cart."""
    cart = get_or_create_cart(request)
    
    # Calculate totals
    subtotal = cart.get_subtotal()
    discount = cart.get_discount_amount()
    total = cart.get_total()
    
    # Apply coupon form
    apply_coupon_form = ApplyCouponForm()
    
    context = {
        'cart': cart,
        'items': cart.items.select_related('product', 'variant').all(),
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'apply_coupon_form': apply_coupon_form,
        'title': _('Shopping Cart'),
    }
    return render(request, 'cart/view.html', context)


@require_http_methods(["POST"])
@csrf_exempt
def add_to_cart(request):
    """Add item to cart."""
    form = AddToCartForm(request.POST)
    
    if not form.is_valid():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
            }, status=400)
        messages.error(request, _('Invalid request.'))
        return redirect('store:home')
    
    product_id = form.cleaned_data.get('product_id')
    variant_id = form.cleaned_data.get('variant_id')
    quantity = form.cleaned_data.get('quantity')
    
    # Get product
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    # Get variant if specified
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, pk=variant_id, product=product, is_active=True)
    
    # Get or create cart
    cart = get_or_create_cart(request)
    
    # Check if item already exists
    existing_item = CartItem.objects.filter(
        cart=cart,
        product=product,
        variant=variant
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += quantity
        existing_item.save()
    else:
        # Create new cart item
        CartItem.objects.create(
            cart=cart,
            product=product,
            variant=variant,
            quantity=quantity
        )
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': _('Added to cart'),
            'cart_item_count': cart.get_item_count(),
            'cart_total': cart.get_total(),
        })
    
    messages.success(request, _('Product has been added to your cart!'))
    return redirect('cart:view')


@require_http_methods(["POST"])
@csrf_exempt
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    form = UpdateCartItemForm(request.POST)
    
    if not form.is_valid():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
            }, status=400)
        return redirect('cart:view')
    
    item_id = form.cleaned_data.get('item_id')
    quantity = form.cleaned_data.get('quantity')
    
    # Get cart item
    cart_item = get_object_or_404(CartItem, pk=item_id)
    
    # Check if item belongs to user's cart
    cart = get_or_create_cart(request)
    if cart_item.cart != cart:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Invalid cart item'}, status=400)
        return redirect('cart:view')
    
    # Update quantity
    cart_item.quantity = quantity
    cart_item.save()
    
    # Return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_total': cart_item.get_subtotal(),
            'cart_subtotal': cart.get_subtotal(),
            'cart_discount': cart.get_discount_amount(),
            'cart_total': cart.get_total(),
        })
    
    return redirect('cart:view')


@require_http_methods(["POST"])
@csrf_exempt
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_item_count': cart.get_item_count(),
            'cart_subtotal': cart.get_subtotal(),
            'cart_discount': cart.get_discount_amount(),
            'cart_total': cart.get_total(),
        })
    
    messages.success(request, _('Item has been removed from your cart!'))
    return redirect('cart:view')


@require_http_methods(["POST"])
@csrf_exempt
def clear_cart(request):
    """Clear all items from cart."""
    cart = get_or_create_cart(request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        confirm = request.POST.get('confirm')
        if not confirm:
            return JsonResponse({'success': False, 'error': 'Confirmation required'}, status=400)
    
    cart.clear()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_item_count': 0,
            'cart_total': 0,
        })
    
    messages.success(request, _('Your cart has been cleared!'))
    return redirect('cart:view')


@require_http_methods(["POST"])
@csrf_exempt
def apply_coupon(request):
    """Apply coupon to cart."""
    form = ApplyCouponForm(request.POST)
    
    if not form.is_valid():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
            }, status=400)
        return redirect('cart:view')
    
    coupon_code = form.cleaned_data.get('coupon_code')
    cart = get_or_create_cart(request)
    
    # Check if coupon exists and is valid
    try:
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        
        if not coupon.is_valid():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': _('This coupon is not valid or has expired.'),
                }, status=400)
            messages.error(request, _('This coupon is not valid or has expired.'))
            return redirect('cart:view')
        
        # Check if coupon is valid for this cart
        # This would need more complex logic based on your requirements
        # For now, just apply it
        cart.coupon = coupon
        cart.save()
        
        discount = cart.get_discount_amount()
        total = cart.get_total()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': _('Coupon applied successfully!'),
                'coupon_code': coupon_code,
                'discount': discount,
                'total': total,
            })
        
        messages.success(request, _('Coupon applied successfully!'))
        return redirect('cart:view')
        
    except Coupon.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': _('Invalid coupon code.'),
            }, status=400)
        messages.error(request, _('Invalid coupon code.'))
        return redirect('cart:view')


@require_http_methods(["POST"])
@csrf_exempt
def remove_coupon(request):
    """Remove coupon from cart."""
    cart = get_or_create_cart(request)
    
    if cart.coupon:
        cart.coupon = None
        cart.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_subtotal': cart.get_subtotal(),
            'cart_discount': 0,
            'cart_total': cart.get_total(),
        })
    
    messages.success(request, _('Coupon has been removed!'))
    return redirect('cart:view')


@require_http_methods(["GET"])
def get_cart_summary(request):
    """Get cart summary for header/mini-cart."""
    cart = get_or_create_cart(request)
    
    return JsonResponse({
        'item_count': cart.get_item_count(),
        'unique_item_count': cart.get_unique_item_count(),
        'subtotal': cart.get_subtotal(),
        'discount': cart.get_discount_amount(),
        'total': cart.get_total(),
        'items': [
            {
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'variant_name': item.variant.name if item.variant else None,
                'quantity': item.quantity,
                'price': item.get_price(),
                'subtotal': item.get_subtotal(),
                'image': item.product.featured_image.url if item.product.featured_image else None,
            }
            for item in cart.items.select_related('product', 'variant').all()
        ],
    })
