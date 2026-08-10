"""
Views for orders app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction

from .models import Order, OrderItem, Refund
from .forms import (
    CheckoutForm, OrderCancelForm, RefundRequestForm,
    OrderNoteForm, OrderStatusForm, BulkOrderUpdateForm
)
from apps.cart.models import Cart
from apps.products.models import Product, ProductVariant
from apps.shipping.models import ShippingMethod
from apps.payments.models import PaymentGateway, Transaction
from apps.discounts.models import Coupon
import uuid


def get_cart_for_checkout(request):
    """Get cart for checkout."""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, cart_type='user').first()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key, cart_type='session').first()
        else:
            cart = None
    
    if not cart or cart.get_item_count() == 0:
        raise Http404(_('Your cart is empty'))
    
    return cart


@login_required
@require_http_methods(["GET"])
def checkout(request):
    """Checkout view - Step 1: Address Information."""
    cart = get_cart_for_checkout(request)
    
    # Get shipping methods
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    
    # Get payment gateways
    payment_gateways = PaymentGateway.objects.filter(is_active=True)
    
    # Initialize form with user data
    initial_data = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'phone_number': request.user.phone_number,
    }
    
    # If user has default address, use it
    default_address = request.user.addresses.filter(is_default=True).first()
    if default_address:
        initial_data.update({
            'shipping_address_line_1': default_address.address_line_1,
            'shipping_address_line_2': default_address.address_line_2,
            'shipping_city': default_address.city,
            'shipping_state': default_address.state,
            'shipping_postal_code': default_address.postal_code,
            'shipping_country': default_address.country,
        })
    
    form = CheckoutForm(initial=initial_data)
    
    context = {
        'cart': cart,
        'form': form,
        'shipping_methods': shipping_methods,
        'payment_gateways': payment_gateways,
        'step': 1,
        'title': _('Checkout - Address Information'),
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@require_http_methods(["POST"])
def checkout_address(request):
    """Checkout Step 1: Process address information."""
    cart = get_cart_for_checkout(request)
    
    form = CheckoutForm(data=request.POST)
    if not form.is_valid():
        messages.error(request, _('Please correct the errors below.'))
        return redirect('orders:checkout')
    
    # Store address data in session
    request.session['checkout_data'] = form.cleaned_data
    
    return redirect('orders:checkout_shipping')


@login_required
@require_http_methods(["GET", "POST"])
def checkout_shipping(request):
    """Checkout Step 2: Shipping Method."""
    cart = get_cart_for_checkout(request)
    
    # Get checkout data from session
    checkout_data = request.session.get('checkout_data', {})
    if not checkout_data:
        return redirect('orders:checkout')
    
    # Get shipping methods
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    
    if request.method == 'POST':
        shipping_method_id = request.POST.get('shipping_method')
        try:
            shipping_method = ShippingMethod.objects.get(pk=shipping_method_id, is_active=True)
            checkout_data['shipping_method'] = shipping_method.id
            request.session['checkout_data'] = checkout_data
            return redirect('orders:checkout_payment')
        except ShippingMethod.DoesNotExist:
            messages.error(request, _('Invalid shipping method.'))
    
    # Calculate shipping costs for each method
    shipping_costs = []
    for method in shipping_methods:
        cost = method.calculate_cost(cart)
        shipping_costs.append({
            'method': method,
            'cost': cost,
            'estimated_delivery': method.get_estimated_delivery(),
        })
    
    context = {
        'cart': cart,
        'shipping_methods': shipping_costs,
        'step': 2,
        'title': _('Checkout - Shipping Method'),
    }
    return render(request, 'orders/checkout_shipping.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def checkout_payment(request):
    """Checkout Step 3: Payment Method."""
    cart = get_cart_for_checkout(request)
    
    # Get checkout data from session
    checkout_data = request.session.get('checkout_data', {})
    if not checkout_data or 'shipping_method' not in checkout_data:
        return redirect('orders:checkout')
    
    # Get payment gateways
    payment_gateways = PaymentGateway.objects.filter(is_active=True)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        checkout_data['payment_method'] = payment_method
        request.session['checkout_data'] = checkout_data
        return redirect('orders:checkout_confirm')
    
    context = {
        'cart': cart,
        'payment_gateways': payment_gateways,
        'step': 3,
        'title': _('Checkout - Payment Method'),
    }
    return render(request, 'orders/checkout_payment.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def checkout_confirm(request):
    """Checkout Step 4: Confirm Order."""
    cart = get_cart_for_checkout(request)
    
    # Get checkout data from session
    checkout_data = request.session.get('checkout_data', {})
    if not checkout_data or 'payment_method' not in checkout_data:
        return redirect('orders:checkout')
    
    # Get shipping method
    try:
        shipping_method = ShippingMethod.objects.get(
            pk=checkout_data.get('shipping_method'),
            is_active=True
        )
    except ShippingMethod.DoesNotExist:
        return redirect('orders:checkout_shipping')
    
    # Calculate totals
    subtotal = cart.get_subtotal()
    shipping_cost = shipping_method.calculate_cost(cart) or 0
    discount = cart.get_discount_amount()
    total = subtotal + shipping_cost - discount
    
    if request.method == 'POST':
        # Create order
        try:
            with transaction.atomic():
                # Generate order number
                order_number = f'ORD-{uuid.uuid4().hex[:8].upper()}'
                
                # Create order
                order = Order.objects.create(
                    order_number=order_number,
                    user=request.user,
                    first_name=checkout_data.get('first_name'),
                    last_name=checkout_data.get('last_name'),
                    email=checkout_data.get('email'),
                    phone_number=checkout_data.get('phone_number'),
                    
                    # Shipping address
                    shipping_address_line_1=checkout_data.get('shipping_address_line_1'),
                    shipping_address_line_2=checkout_data.get('shipping_address_line_2'),
                    shipping_city=checkout_data.get('shipping_city'),
                    shipping_state=checkout_data.get('shipping_state'),
                    shipping_postal_code=checkout_data.get('shipping_postal_code'),
                    shipping_country=checkout_data.get('shipping_country'),
                    
                    # Billing address
                    billing_address_line_1=checkout_data.get('billing_address_line_1'),
                    billing_address_line_2=checkout_data.get('billing_address_line_2'),
                    billing_city=checkout_data.get('billing_city'),
                    billing_state=checkout_data.get('billing_state'),
                    billing_postal_code=checkout_data.get('billing_postal_code'),
                    billing_country=checkout_data.get('billing_country'),
                    
                    # Order details
                    subtotal=subtotal,
                    discount=discount,
                    shipping_cost=shipping_cost,
                    total=total,
                    
                    # Coupon
                    coupon=cart.coupon,
                    coupon_discount=discount,
                    
                    # Payment
                    payment_method=checkout_data.get('payment_method'),
                    payment_status='pending',
                    
                    # Shipping
                    shipping_method=shipping_method,
                    
                    # Additional info
                    customer_notes=checkout_data.get('customer_notes', ''),
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                )
                
                # Create order items
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        variant=item.variant,
                        product_name=item.product.name,
                        product_sku=item.product.sku if item.product.sku else str(item.product.id),
                        quantity=item.quantity,
                        price=item.get_price(),
                        subtotal=item.get_subtotal(),
                        product_snapshot={
                            'id': str(item.product.id),
                            'name': item.product.name,
                            'sku': item.product.sku,
                            'price': str(item.get_price()),
                            'image': item.product.featured_image.url if item.product.featured_image else None,
                        }
                    )
                
                # Clear cart
                cart.clear()
                
                # Clear checkout session
                request.session.pop('checkout_data', None)
                
                messages.success(request, _('Your order has been placed successfully!'))
                
                # Redirect based on payment method
                if checkout_data.get('payment_method') == 'online':
                    # Redirect to payment gateway
                    return redirect('payments:process', order_id=order.id)
                else:
                    # For other payment methods, show order confirmation
                    return redirect('orders:order_confirmation', order_number=order.order_number)
        
        except Exception as e:
            messages.error(request, _('There was an error processing your order. Please try again.'))
            return redirect('orders:checkout')
    
    context = {
        'cart': cart,
        'checkout_data': checkout_data,
        'shipping_method': shipping_method,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'discount': discount,
        'total': total,
        'step': 4,
        'title': _('Checkout - Confirm Order'),
    }
    return render(request, 'orders/checkout_confirm.html', context)


@login_required
@require_http_methods(["GET"])
def order_confirmation(request, order_number):
    """Order confirmation page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
        'title': _('Order Confirmation'),
    }
    return render(request, 'orders/order_confirmation.html', context)


@login_required
@require_http_methods(["GET"])
def order_list(request):
    """List user orders."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    
    try:
        orders_page = paginator.page(page)
    except PageNotAnInteger:
        orders_page = paginator.page(1)
    except EmptyPage:
        orders_page = paginator.page(paginator.num_pages)
    
    context = {
        'orders': orders_page,
        'title': _('My Orders'),
    }
    return render(request, 'orders/order_list.html', context)


@login_required
@require_http_methods(["GET"])
def order_detail(request, order_number):
    """Order detail view."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
        'title': _('Order #%(order_number)s') % {'order_number': order_number},
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
@require_http_methods(["POST"])
def order_cancel(request, order_number):
    """Cancel an order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if not order.can_be_cancelled():
        messages.error(request, _('This order cannot be cancelled.'))
        return redirect('orders:order_detail', order_number=order_number)
    
    # Cancel the order
    order.status = 'cancelled'
    order.cancelled_at = timezone.now()
    order.save()
    
    messages.success(request, _('Your order has been cancelled successfully!'))
    return redirect('orders:order_detail', order_number=order_number)


@login_required
@require_http_methods(["GET", "POST"])
def request_refund(request, order_number):
    """Request refund for an order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if not order.can_be_refunded():
        messages.error(request, _('This order cannot be refunded.'))
        return redirect('orders:order_detail', order_number=order_number)
    
    form = RefundRequestForm()
    if request.method == 'POST':
        form = RefundRequestForm(data=request.POST)
        if form.is_valid():
            order_item_id = form.cleaned_data.get('order_item')
            reason = form.cleaned_data.get('reason')
            reason_details = form.cleaned_data.get('reason_details')
            
            try:
                order_item = OrderItem.objects.get(pk=order_item_id, order=order)
                
                # Create refund
                refund = Refund.objects.create(
                    order=order,
                    order_item=order_item,
                    amount=order_item.subtotal,
                    reason=reason,
                    reason_details=reason_details,
                    status='pending',
                )
                
                messages.success(request, _('Your refund request has been submitted successfully!'))
                return redirect('orders:order_detail', order_number=order_number)
            except OrderItem.DoesNotExist:
                messages.error(request, _('Invalid order item.'))
    
    context = {
        'order': order,
        'form': form,
        'title': _('Request Refund'),
    }
    return render(request, 'orders/refund_request.html', context)


# AJAX Views
@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ajax_get_shipping_cost(request):
    """Get shipping cost for selected method."""
    cart = get_cart_for_checkout(request)
    shipping_method_id = request.POST.get('shipping_method_id')
    
    try:
        shipping_method = ShippingMethod.objects.get(pk=shipping_method_id, is_active=True)
        cost = shipping_method.calculate_cost(cart)
        
        return JsonResponse({
            'success': True,
            'cost': cost,
            'formatted_cost': f'{cost:,.0f} تومان' if cost else 'رایگان',
            'estimated_delivery': shipping_method.get_estimated_delivery(),
        })
    except ShippingMethod.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid shipping method'}, status=400)


@login_required
@require_http_methods(["GET"])
def track_order(request, order_number):
    """Track order status."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Get status history
    status_history = order.status_history.select_related('changed_by').all().order_by('-created_at')
    
    context = {
        'order': order,
        'status_history': status_history,
        'title': _('Track Order #%(order_number)s') % {'order_number': order_number},
    }
    return render(request, 'orders/track_order.html', context)
