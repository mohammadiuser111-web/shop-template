"""
Views for payments app.
"""
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, Count
from django.conf import settings

from .models import (
    Payment, PaymentMethod, Transaction, Refund, PaymentGateway,
    Wallet, WalletTransaction
)
from .forms import (
    PaymentMethodForm, WalletTopUpForm, RefundRequestForm,
    PaymentForm
)
from apps.orders.models import Order
from apps.discounts.models import Coupon


# ==================== PAYMENT GATEWAY VIEWS ====================

@login_required
@require_http_methods(["GET", "POST"])
def payment_gateway(request, order_id):
    """Payment gateway selection and processing."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    # Check if order can be paid
    if order.status not in ['pending', 'failed', 'cancelled']:
        messages.error(request, _('This order cannot be paid.'))
        return redirect('orders:order_detail', pk=order_id)
    
    # Get available payment methods
    available_gateways = PaymentGateway.objects.filter(is_active=True)
    
    # Get user's saved payment methods
    saved_methods = PaymentMethod.objects.filter(
        user=request.user,
        is_active=True
    )
    
    if request.method == 'POST':
        gateway_id = request.POST.get('gateway')
        payment_method_id = request.POST.get('payment_method')
        use_new_card = request.POST.get('use_new_card') == '1'
        
        gateway = get_object_or_404(PaymentGateway, pk=gateway_id, is_active=True)
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            gateway=gateway,
            amount=order.total_amount,
            currency=order.currency,
            status='pending',
            transaction_id=f'PAY-{uuid.uuid4().hex[:12].upper()}',
        )
        
        # Handle different payment methods
        if use_new_card:
            # Process new card payment
            return process_new_card_payment(request, order, payment, gateway)
        elif payment_method_id:
            # Use saved payment method
            saved_method = get_object_or_404(PaymentMethod, pk=payment_method_id, user=request.user)
            return process_saved_payment(request, order, payment, gateway, saved_method)
        else:
            # Redirect to gateway
            return redirect_to_gateway(request, order, payment, gateway)
    
    context = {
        'order': order,
        'gateways': available_gateways,
        'saved_methods': saved_methods,
        'title': _('Payment Gateway'),
    }
    return render(request, 'payments/payment_gateway.html', context)


def process_new_card_payment(request, order, payment, gateway):
    """Process payment with new card."""
    # In a real implementation, this would integrate with the payment gateway API
    # For demo purposes, we'll simulate the process
    
    # Get card details from form
    card_number = request.POST.get('card_number')
    expiry_month = request.POST.get('expiry_month')
    expiry_year = request.POST.get('expiry_year')
    cvv = request.POST.get('cvv')
    card_holder = request.POST.get('card_holder')
    save_card = request.POST.get('save_card') == '1'
    
    # Simulate payment processing
    # In production, you would:
    # 1. Send request to payment gateway API
    # 2. Get token/response
    # 3. Process the payment
    # 4. Handle the response
    
    # For demo, simulate successful payment
    import random
    success = random.random() > 0.2  # 80% success rate for demo
    
    if success:
        # Payment successful
        payment.status = 'completed'
        payment.save()
        
        # Update order status
        order.status = 'paid'
        order.payment_status = 'paid'
        order.save()
        
        # Save card if requested
        if save_card and card_number:
            PaymentMethod.objects.create(
                user=request.user,
                gateway=gateway,
                card_type='credit' if card_number.startswith('4') else 'debit',
                last_four=card_number[-4:],
                card_holder=card_holder,
                is_default=False,
            )
        
        # Create transaction
        Transaction.objects.create(
            payment=payment,
            amount=payment.amount,
            currency=payment.currency,
            status='completed',
            gateway_response='Payment successful',
            transaction_id=payment.transaction_id,
        )
        
        messages.success(request, _('Payment successful! Your order has been placed.'))
        return redirect('orders:order_confirmation', pk=order.pk)
    else:
        # Payment failed
        payment.status = 'failed'
        payment.failure_reason = 'Insufficient funds'
        payment.save()
        
        Transaction.objects.create(
            payment=payment,
            amount=payment.amount,
            currency=payment.currency,
            status='failed',
            gateway_response='Insufficient funds',
            transaction_id=payment.transaction_id,
        )
        
        messages.error(request, _('Payment failed. Please try again.'))
        return redirect('payments:payment_gateway', order_id=order.pk)


def process_saved_payment(request, order, payment, gateway, saved_method):
    """Process payment with saved payment method."""
    # In a real implementation, use the saved token
    # For demo, simulate the process
    
    import random
    success = random.random() > 0.2
    
    if success:
        payment.status = 'completed'
        payment.save()
        
        order.status = 'paid'
        order.payment_status = 'paid'
        order.save()
        
        Transaction.objects.create(
            payment=payment,
            amount=payment.amount,
            currency=payment.currency,
            status='completed',
            gateway_response='Payment successful with saved method',
            transaction_id=payment.transaction_id,
        )
        
        messages.success(request, _('Payment successful!'))
        return redirect('orders:order_confirmation', pk=order.pk)
    else:
        payment.status = 'failed'
        payment.save()
        
        Transaction.objects.create(
            payment=payment,
            amount=payment.amount,
            currency=payment.currency,
            status='failed',
            gateway_response='Payment failed',
            transaction_id=payment.transaction_id,
        )
        
        messages.error(request, _('Payment failed. Please try another method.'))
        return redirect('payments:payment_gateway', order_id=order.pk)


def redirect_to_gateway(request, order, payment, gateway):
    """Redirect to external payment gateway."""
    # In a real implementation, this would redirect to the gateway
    # For demo, we'll just show a confirmation page
    
    context = {
        'order': order,
        'payment': payment,
        'gateway': gateway,
        'title': _('Redirecting to Payment Gateway'),
    }
    return render(request, 'payments/redirect_to_gateway.html', context)


# ==================== PAYMENT CALLBACKS ====================

@csrf_exempt
@require_http_methods(["POST"])
def payment_callback(request, gateway_name):
    """Handle payment gateway callback."""
    # In a real implementation, verify the callback signature
    # and process the payment status
    
    gateway = get_object_or_404(PaymentGateway, name=gateway_name, is_active=True)
    
    # Get payment from request
    transaction_id = request.POST.get('transaction_id')
    status = request.POST.get('status')
    amount = request.POST.get('amount')
    
    try:
        payment = Payment.objects.get(transaction_id=transaction_id)
        
        if status == 'completed':
            payment.status = 'completed'
            payment.save()
            
            # Update order
            payment.order.status = 'paid'
            payment.order.payment_status = 'paid'
            payment.order.save()
            
            # Create transaction
            Transaction.objects.create(
                payment=payment,
                amount=amount,
                currency=payment.currency,
                status='completed',
                gateway_response='Payment completed via callback',
                transaction_id=transaction_id,
            )
            
            return JsonResponse({'status': 'success'})
        elif status == 'failed':
            payment.status = 'failed'
            payment.failure_reason = request.POST.get('reason', 'Payment failed')
            payment.save()
            
            Transaction.objects.create(
                payment=payment,
                amount=amount,
                currency=payment.currency,
                status='failed',
                gateway_response=payment.failure_reason,
                transaction_id=transaction_id,
            )
            
            return JsonResponse({'status': 'failed'})
        
    except Payment.DoesNotExist:
        pass
    
    return JsonResponse({'status': 'error', 'message': 'Invalid transaction'}, status=400)


@require_http_methods(["GET"])
def payment_success(request, payment_id):
    """Payment success page."""
    payment = get_object_or_404(Payment, pk=payment_id)
    
    if payment.status != 'completed':
        return redirect('payments:payment_failed', payment_id=payment_id)
    
    context = {
        'payment': payment,
        'title': _('Payment Successful'),
    }
    return render(request, 'payments/payment_success.html', context)


@require_http_methods(["GET"])
def payment_failed(request, payment_id):
    """Payment failed page."""
    payment = get_object_or_404(Payment, pk=payment_id)
    
    context = {
        'payment': payment,
        'title': _('Payment Failed'),
    }
    return render(request, 'payments/payment_failed.html', context)


# ==================== PAYMENT METHODS ====================

@login_required
@require_http_methods(["GET", "POST"])
def payment_methods(request):
    """Manage user's payment methods."""
    methods = PaymentMethod.objects.filter(
        user=request.user
    ).select_related('gateway').order_by('-is_default', '-created_at')
    
    if request.method == 'POST':
        form = PaymentMethodForm(data=request.POST)
        if form.is_valid():
            method = PaymentMethod.objects.create(
                user=request.user,
                gateway=form.cleaned_data.get('gateway'),
                card_type=form.cleaned_data.get('card_type'),
                last_four=form.cleaned_data.get('last_four'),
                card_holder=form.cleaned_data.get('card_holder'),
                expiry_month=form.cleaned_data.get('expiry_month'),
                expiry_year=form.cleaned_data.get('expiry_year'),
                is_default=form.cleaned_data.get('is_default'),
            )
            
            # If this is the first method, make it default
            if not methods.exists():
                method.is_default = True
                method.save()
            
            messages.success(request, _('Payment method added successfully.'))
            return redirect('payments:payment_methods')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = PaymentMethodForm()
    
    context = {
        'methods': methods,
        'form': form,
        'title': _('Payment Methods'),
    }
    return render(request, 'payments/payment_methods.html', context)


@login_required
@require_http_methods(["POST"])
def delete_payment_method(request, method_id):
    """Delete a payment method."""
    method = get_object_or_404(PaymentMethod, pk=method_id, user=request.user)
    
    method.is_active = False
    method.save()
    
    messages.success(request, _('Payment method deleted.'))
    return redirect('payments:payment_methods')


@login_required
@require_http_methods(["POST"])
def set_default_payment_method(request, method_id):
    """Set a payment method as default."""
    method = get_object_or_404(PaymentMethod, pk=method_id, user=request.user)
    
    # Clear default from all other methods
    PaymentMethod.objects.filter(
        user=request.user
    ).update(is_default=False)
    
    # Set this as default
    method.is_default = True
    method.save()
    
    messages.success(request, _('Default payment method updated.'))
    return redirect('payments:payment_methods')


# ==================== WALLET ====================

@login_required
@require_http_methods(["GET"])
def wallet(request):
    """User's wallet page."""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Get transactions
    transactions = WalletTransaction.objects.filter(
        wallet=wallet
    ).select_related('payment').order_by('-created_at')[:20]
    
    # Get balance
    balance = wallet.balance
    
    # Get top-up form
    top_up_form = WalletTopUpForm()
    
    context = {
        'wallet': wallet,
        'balance': balance,
        'transactions': transactions,
        'top_up_form': top_up_form,
        'title': _('My Wallet'),
    }
    return render(request, 'payments/wallet.html', context)


@login_required
@require_http_methods(["POST"])
def wallet_top_up(request):
    """Top up wallet."""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    form = WalletTopUpForm(data=request.POST)
    if form.is_valid():
        amount = form.cleaned_data.get('amount')
        
        # Create pending transaction
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type='credit',
            status='pending',
            description=f'Top up ${amount}',
            reference_id=f'TOPUP-{uuid.uuid4().hex[:12].upper()}',
        )
        
        # In a real implementation, redirect to payment gateway
        # For demo, simulate immediate credit
        transaction.status = 'completed'
        transaction.save()
        
        wallet.balance += amount
        wallet.save()
        
        messages.success(request, _('Your wallet has been topped up.'))
    else:
        messages.error(request, _('Please correct the errors below.'))
    
    return redirect('payments:wallet')


@login_required
@require_http_methods(["GET"])
def wallet_transactions(request):
    """Wallet transaction history."""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    transactions = WalletTransaction.objects.filter(
        wallet=wallet
    ).select_related('payment').order_by('-created_at')
    
    # Filter by type
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page')
    
    try:
        transactions_page = paginator.page(page)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)
    
    context = {
        'wallet': wallet,
        'transactions': transactions_page,
        'current_type': transaction_type,
        'title': _('Wallet Transactions'),
    }
    return render(request, 'payments/wallet_transactions.html', context)


# ==================== REFUNDS ====================

@login_required
@require_http_methods(["GET"])
def refunds(request):
    """List user's refund requests."""
    refunds = Refund.objects.filter(
        user=request.user
    ).select_related('payment__order').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(refunds, 10)
    page = request.GET.get('page')
    
    try:
        refunds_page = paginator.page(page)
    except PageNotAnInteger:
        refunds_page = paginator.page(1)
    except EmptyPage:
        refunds_page = paginator.page(paginator.num_pages)
    
    context = {
        'refunds': refunds_page,
        'title': _('My Refunds'),
    }
    return render(request, 'payments/refunds.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def request_refund(request, payment_id):
    """Request a refund for a payment."""
    payment = get_object_or_404(Payment, pk=payment_id, user=request.user)
    
    # Check if refund is possible
    if payment.status != 'completed':
        messages.error(request, _('Refund is not available for this payment.'))
        return redirect('payments:refunds')
    
    # Check if already requested
    existing_refund = Refund.objects.filter(
        payment=payment,
        user=request.user
    ).first()
    
    if existing_refund:
        messages.error(request, _('You have already requested a refund for this payment.'))
        return redirect('payments:refunds')
    
    if request.method == 'POST':
        form = RefundRequestForm(data=request.POST)
        if form.is_valid():
            refund = Refund.objects.create(
                payment=payment,
                user=request.user,
                amount=form.cleaned_data.get('amount'),
                reason=form.cleaned_data.get('reason'),
                description=form.cleaned_data.get('description'),
                status='pending',
                reference_id=f'REF-{uuid.uuid4().hex[:12].upper()}',
            )
            
            messages.success(request, _('Your refund request has been submitted.'))
            return redirect('payments:refunds')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = RefundRequestForm()
    
    context = {
        'payment': payment,
        'form': form,
        'title': _('Request Refund'),
    }
    return render(request, 'payments/request_refund.html', context)


@login_required
@require_http_methods(["GET"])
def refund_detail(request, refund_id):
    """Refund detail page."""
    refund = get_object_or_404(Refund, pk=refund_id, user=request.user)
    
    context = {
        'refund': refund,
        'title': f"{_('Refund')} #{refund.reference_id}",
    }
    return render(request, 'payments/refund_detail.html', context)


# ==================== PAYMENT HISTORY ====================

@login_required
@require_http_methods(["GET"])
def payment_history(request):
    """User's payment history."""
    payments = Payment.objects.filter(
        user=request.user
    ).select_related('order', 'gateway').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Filter by gateway
    gateway_filter = request.GET.get('gateway')
    if gateway_filter:
        payments = payments.filter(gateway__id=gateway_filter)
    
    # Pagination
    paginator = Paginator(payments, 10)
    page = request.GET.get('page')
    
    try:
        payments_page = paginator.page(page)
    except PageNotAnInteger:
        payments_page = paginator.page(1)
    except EmptyPage:
        payments_page = paginator.page(paginator.num_pages)
    
    gateways = PaymentGateway.objects.filter(is_active=True)
    
    context = {
        'payments': payments_page,
        'gateways': gateways,
        'current_status': status_filter,
        'current_gateway': gateway_filter,
        'title': _('Payment History'),
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
@require_http_methods(["GET"])
def payment_detail(request, payment_id):
    """Payment detail page."""
    payment = get_object_or_404(Payment, pk=payment_id, user=request.user)
    
    transactions = Transaction.objects.filter(
        payment=payment
    ).order_by('-created_at')
    
    context = {
        'payment': payment,
        'transactions': transactions,
        'title': f"{_('Payment')} #{payment.transaction_id}",
    }
    return render(request, 'payments/payment_detail.html', context)


# ==================== AJAX VIEWS ====================

@login_required
@require_http_methods(["GET"])
def get_payment_status_ajax(request, payment_id):
    """Get payment status via AJAX."""
    payment = get_object_or_404(Payment, pk=payment_id)
    
    if payment.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return JsonResponse({
        'status': payment.status,
        'amount': payment.amount,
        'currency': payment.currency,
        'created_at': payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'gateway': payment.gateway.name if payment.gateway else None,
    })


@login_required
@require_http_methods(["GET"])
def get_wallet_balance_ajax(request):
    """Get wallet balance via AJAX."""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    return JsonResponse({
        'balance': wallet.balance,
        'currency': 'USD',
    })


@login_required
@require_http_methods(["POST"])
def verify_payment_ajax(request):
    """Verify payment via AJAX."""
    payment_id = request.POST.get('payment_id')
    
    payment = get_object_or_404(Payment, pk=payment_id)
    
    if payment.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # In a real implementation, verify with the gateway
    # For demo, return the current status
    return JsonResponse({
        'status': payment.status,
        'verified': payment.status == 'completed',
    })


@require_http_methods(["GET"])
def get_available_gateways_ajax(request):
    """Get available payment gateways via AJAX."""
    gateways = PaymentGateway.objects.filter(is_active=True)
    
    gateways_data = []
    for gateway in gateways:
        gateways_data.append({
            'id': str(gateway.id),
            'name': gateway.name,
            'display_name': gateway.display_name,
            'logo': gateway.logo.url if gateway.logo else None,
            'description': gateway.description,
            'fees': gateway.fees,
            'supported_currencies': gateway.supported_currencies,
        })
    
    return JsonResponse({'gateways': gateways_data})
