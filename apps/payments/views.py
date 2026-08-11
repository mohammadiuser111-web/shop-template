"""
Views for payments app.
Integrates with Iranian payment gateways (Zarinpal, IDPay, Pay.ir, NextPay).
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

from .models import PaymentGateway, Transaction, Wallet, WalletTransaction
from .forms import (
    PaymentGatewayForm,
    WalletDepositForm,
    WalletWithdrawForm,
    PaymentForm,
    RefundForm,
    PaymentSearchForm,
)
from .services import PaymentService
from apps.orders.models import Order


# ==================== PAYMENT GATEWAY VIEWS ====================

@login_required
def payment_gateway_select(request):
    """Select payment gateway for an order."""
    order_id = request.GET.get('order_id')
    
    if not order_id:
        messages.error(request, _(' Order ID is required.'))
        return redirect('store:home')
    
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    # Check if order can be paid
    if order.status not in ['pending', 'failed', 'cancelled']:
        messages.error(request, _('این سفارش قابل پرداخت نیست.'))
        return redirect('orders:order_detail', pk=order_id)
    
    # Get available gateways
    gateways = PaymentService.get_active_gateways()
    
    if request.method == 'POST':
        gateway_type = request.POST.get('gateway')
        
        if not gateway_type:
            messages.error(request, _('لطفاً یک درگاه پرداخت انتخاب کنید.'))
            return redirect('payments:select_gateway')
        
        # Create transaction
        transaction, result = PaymentService.create_payment(
            order=order,
            user=request.user,
            gateway_type=gateway_type,
            amount=order.total_amount,
            currency='IRR',
            description=f'پرداخت سفارش #{order.code}'
        )
        
        if not result['success']:
            messages.error(request, result.get('message', _('خطا در ایجاد تراکنش')))
            return redirect('payments:select_gateway')
        
        # Process payment
        redirect_url, result = PaymentService.process_payment(transaction, gateway_type)
        
        if result['success'] and redirect_url:
            return redirect(redirect_url)
        else:
            messages.error(request, result.get('message', _('خطا در اتصال به درگاه')))
            return redirect('payments:select_gateway')
    
    context = {
        'order': order,
        'gateways': gateways,
        'page_title': _('انتخاب درگاه پرداخت'),
    }
    return render(request, 'payments/payment_gateway.html', context)


@login_required
def payment_process(request, gateway_type):
    """Process payment for a specific gateway."""
    order_id = request.GET.get('order_id')
    
    if not order_id:
        return JsonResponse({'success': False, 'message': 'Order ID is required'}, status=400)
    
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    # Create transaction
    transaction, result = PaymentService.create_payment(
        order=order,
        user=request.user,
        gateway_type=gateway_type,
        amount=order.total_amount,
        currency='IRR',
        description=f'پرداخت سفارش #{order.code}'
    )
    
    if not result['success']:
        return JsonResponse({'success': False, 'message': result.get('message')})
    
    # Process payment
    redirect_url, result = PaymentService.process_payment(transaction, gateway_type)
    
    if result['success'] and redirect_url:
        return JsonResponse({'success': True, 'redirect_url': redirect_url})
    else:
        return JsonResponse({'success': False, 'message': result.get('message')})


# ==================== CALLBACK VIEWS ====================

@csrf_exempt
def zarinpal_callback(request):
    """Handle Zarinpal callback."""
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    
    if status != 'OK':
        transaction = Transaction.objects.filter(gateway_reference=authority).first()
        if transaction:
            transaction.status = 'failed'
            transaction.error_message = f'Status: {status}'
            transaction.save()
        return render(request, 'payments/payment_failed.html', {
            'message': _('پرداخت ناموفق بود'),
            'page_title': _('خطا در پرداخت')
        })
    
    # Verify payment
    transaction, result = PaymentService.verify_payment(
        'zarinpal',
        {'Authority': authority, 'Status': status}
    )
    
    if transaction and result['success']:
        # Update order status
        if transaction.order:
            transaction.order.status = 'paid'
            transaction.order.payment_status = 'paid'
            transaction.order.save()
        
        return render(request, 'payments/payment_success.html', {
            'transaction': transaction,
            'ref_id': result.get('ref_id'),
            'page_title': _('پرداخت موفق')
        })
    else:
        return render(request, 'payments/payment_failed.html', {
            'message': result.get('message', _('تایید پرداخت ناموفق بود')),
            'page_title': _('خطا در پرداخت')
        })


@csrf_exempt
def idpay_callback(request):
    """Handle IDPay callback."""
    order_id = request.GET.get('order_id')
    id = request.GET.get('id')
    status = request.GET.get('status')
    
    if status != '10':
        transaction = Transaction.objects.filter(transaction_id=order_id).first()
        if transaction:
            transaction.status = 'failed'
            transaction.error_message = f'Status: {status}'
            transaction.save()
        return render(request, 'payments/payment_failed.html', {
            'message': _('پرداخت ناموفق بود'),
            'page_title': _('خطا در پرداخت')
        })
    
    # Verify payment
    transaction, result = PaymentService.verify_payment(
        'idpay',
        {'order_id': order_id, 'id': id, 'status': status}
    )
    
    if transaction and result['success']:
        # Update order status
        if transaction.order:
            transaction.order.status = 'paid'
            transaction.order.payment_status = 'paid'
            transaction.order.save()
        
        return render(request, 'payments/payment_success.html', {
            'transaction': transaction,
            'page_title': _('پرداخت موفق')
        })
    else:
        return render(request, 'payments/payment_failed.html', {
            'message': result.get('message', _('تایید پرداخت ناموفق بود')),
            'page_title': _('خطا در پرداخت')
        })


@csrf_exempt
def payir_callback(request):
    """Handle Pay.ir callback."""
    token = request.GET.get('token')
    status = request.GET.get('status')
    
    if status != '1':
        transaction = Transaction.objects.filter(gateway_reference=token).first()
        if transaction:
            transaction.status = 'failed'
            transaction.error_message = f'Status: {status}'
            transaction.save()
        return render(request, 'payments/payment_failed.html', {
            'message': _('پرداخت ناموفق بود'),
            'page_title': _('خطا در پرداخت')
        })
    
    # Verify payment
    transaction, result = PaymentService.verify_payment(
        'payir',
        {'token': token, 'status': status}
    )
    
    if transaction and result['success']:
        # Update order status
        if transaction.order:
            transaction.order.status = 'paid'
            transaction.order.payment_status = 'paid'
            transaction.order.save()
        
        return render(request, 'payments/payment_success.html', {
            'transaction': transaction,
            'page_title': _('پرداخت موفق')
        })
    else:
        return render(request, 'payments/payment_failed.html', {
            'message': result.get('message', _('تایید پرداخت ناموفق بود')),
            'page_title': _('خطا در پرداخت')
        })


@csrf_exempt
def nextpay_callback(request):
    """Handle NextPay callback."""
    trans_id = request.GET.get('trans_id')
    order_id = request.GET.get('order_id')
    
    # Verify payment
    transaction, result = PaymentService.verify_payment(
        'nextpay',
        {'trans_id': trans_id, 'order_id': order_id}
    )
    
    if transaction and result['success']:
        # Update order status
        if transaction.order:
            transaction.order.status = 'paid'
            transaction.order.payment_status = 'paid'
            transaction.order.save()
        
        return render(request, 'payments/payment_success.html', {
            'transaction': transaction,
            'page_title': _('پرداخت موفق')
        })
    else:
        return render(request, 'payments/payment_failed.html', {
            'message': result.get('message', _('تایید پرداخت ناموفق بود')),
            'page_title': _('خطا در پرداخت')
        })


# ==================== WALLET VIEWS ====================

@login_required
def wallet_view(request):
    """User's wallet page."""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Get recent transactions
    transactions = WalletTransaction.objects.filter(
        wallet=wallet
    ).select_related('transaction').order_by('-created_at')[:10]
    
    # Forms
    deposit_form = WalletDepositForm()
    withdraw_form = WalletWithdrawForm()
    withdraw_form.context = {'user': request.user}
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
        'deposit_form': deposit_form,
        'withdraw_form': withdraw_form,
        'page_title': _('کیف پول من'),
    }
    return render(request, 'payments/wallet.html', context)


@login_required
@require_http_methods(["POST"])
def wallet_deposit(request):
    """Deposit money to wallet."""
    form = WalletDepositForm(data=request.POST)
    
    if not form.is_valid():
        messages.error(request, _('لطفاً مقادیر را صحیح وارد کنید.'))
        return redirect('payments:wallet')
    
    amount = form.cleaned_data['amount']
    description = form.cleaned_data.get('description', '')
    
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # For demo: directly add to wallet
    # In production: create a transaction and redirect to payment gateway
    try:
        wallet.add_balance(amount, description)
        messages.success(request, _('موجودی کیف پول با موفقیت افزایش یافت.'))
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('payments:wallet')


@login_required
@require_http_methods(["POST"])
def wallet_withdraw(request):
    """Withdraw money from wallet."""
    form = WalletWithdrawForm(data=request.POST)
    form.context = {'user': request.user}
    
    if not form.is_valid():
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
        return redirect('payments:wallet')
    
    amount = form.cleaned_data['amount']
    description = form.cleaned_data.get('description', '')
    
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    try:
        wallet.subtract_balance(amount, description)
        messages.success(request, _('برداشت از کیف پول با موفقیت انجام شد.'))
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('payments:wallet')


@login_required
def wallet_transactions(request):
    """Wallet transaction history."""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    transactions = WalletTransaction.objects.filter(
        wallet=wallet
    ).select_related('transaction').order_by('-created_at')
    
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
        'page_title': _('تاریخچه تراکنش‌های کیف پول'),
    }
    return render(request, 'payments/wallet_transactions.html', context)


# ==================== PAYMENT HISTORY VIEWS ====================

@login_required
def payment_history(request):
    """User's payment history."""
    transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('order', 'gateway').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    # Filter by gateway
    gateway_filter = request.GET.get('gateway')
    if gateway_filter:
        transactions = transactions.filter(gateway__id=gateway_filter)
    
    # Pagination
    paginator = Paginator(transactions, 10)
    page = request.GET.get('page')
    
    try:
        transactions_page = paginator.page(page)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)
    
    gateways = PaymentGateway.objects.filter(is_active=True)
    
    context = {
        'transactions': transactions_page,
        'gateways': gateways,
        'current_status': status_filter,
        'current_gateway': gateway_filter,
        'page_title': _('تاریخچه پرداخت‌ها'),
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def payment_detail(request, transaction_id):
    """Payment detail page."""
    transaction = get_object_or_404(Transaction, pk=transaction_id, user=request.user)
    
    context = {
        'transaction': transaction,
        'page_title': f"{_('جزئیات تراکنش')} #{transaction.transaction_id}",
    }
    return render(request, 'payments/payment_detail.html', context)


@login_required
def payment_receipt(request, transaction_id):
    """Payment receipt page."""
    transaction = get_object_or_404(Transaction, pk=transaction_id, user=request.user)
    
    context = {
        'transaction': transaction,
        'page_title': f"{_('رسید پرداخت')} #{transaction.transaction_id}",
    }
    return render(request, 'payments/receipt.html', context)


# ==================== PAYMENT GATEWAY MANAGEMENT (ADMIN) ====================

@login_required
def payment_gateway_list(request):
    """List all payment gateways (admin view)."""
    if not request.user.is_staff:
        return redirect('store:home')
    
    gateways = PaymentGateway.objects.all().order_by('sort_order')
    
    context = {
        'gateways': gateways,
        'page_title': _('مدیریت درگاه‌های پرداخت'),
    }
    return render(request, 'admin_panel/payment_method_list.html', context)


@login_required
def payment_gateway_create(request):
    """Create a new payment gateway (admin view)."""
    if not request.user.is_staff:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = PaymentGatewayForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            gateway = form.save()
            messages.success(request, _('درگاه پرداخت با موفقیت ایجاد شد.'))
            return redirect('payments:gateway_list')
        else:
            messages.error(request, _('لطفاً خطاهای زیر را اصلاح کنید.'))
    else:
        form = PaymentGatewayForm()
    
    context = {
        'form': form,
        'page_title': _('ایجاد درگاه پرداخت'),
    }
    return render(request, 'admin_panel/payment_gateway_form.html', context)


@login_required
def payment_gateway_edit(request, gateway_id):
    """Edit a payment gateway (admin view)."""
    if not request.user.is_staff:
        return redirect('store:home')
    
    gateway = get_object_or_404(PaymentGateway, pk=gateway_id)
    
    if request.method == 'POST':
        form = PaymentGatewayForm(data=request.POST, files=request.FILES, instance=gateway)
        if form.is_valid():
            form.save()
            messages.success(request, _('درگاه پرداخت با موفقیت بروزرسانی شد.'))
            return redirect('payments:gateway_list')
        else:
            messages.error(request, _('لطفاً خطاهای زیر را اصلاح کنید.'))
    else:
        form = PaymentGatewayForm(instance=gateway)
    
    context = {
        'form': form,
        'gateway': gateway,
        'page_title': _('ویرایش درگاه پرداخت'),
    }
    return render(request, 'admin_panel/payment_gateway_form.html', context)


@login_required
def payment_gateway_toggle(request, gateway_id):
    """Toggle payment gateway active status (admin view)."""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    
    gateway = get_object_or_404(PaymentGateway, pk=gateway_id)
    gateway.is_active = not gateway.is_active
    gateway.save()
    
    return JsonResponse({
        'success': True,
        'is_active': gateway.is_active
    })


# ==================== WEBHOOK VIEWS ====================

@csrf_exempt
def payment_webhook(request, gateway_type):
    """Handle payment gateway webhook."""
    # In a real implementation, verify the webhook signature
    # and process the payment status update
    
    data = json.loads(request.body)
    
    # Verify with the gateway service
    transaction, result = PaymentService.verify_payment(gateway_type, data)
    
    if transaction and result['success']:
        # Update order status
        if transaction.order:
            transaction.order.status = 'paid'
            transaction.order.payment_status = 'paid'
            transaction.order.save()
        
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failed'}, status=400)


# ==================== AJAX VIEWS ====================

@login_required
@require_http_methods(["GET"])
def get_wallet_balance_ajax(request):
    """Get wallet balance via AJAX."""
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    return JsonResponse({
        'success': True,
        'balance': float(wallet.balance),
        'currency': 'IRR',
    })


@login_required
@require_http_methods(["GET"])
def get_payment_status_ajax(request, transaction_id):
    """Get payment status via AJAX."""
    transaction = get_object_or_404(Transaction, pk=transaction_id, user=request.user)
    
    return JsonResponse({
        'success': True,
        'status': transaction.status,
        'amount': float(transaction.amount),
        'currency': transaction.currency,
        'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'gateway': transaction.gateway.name if transaction.gateway else None,
        'gateway_reference': transaction.gateway_reference,
        'error_message': transaction.error_message,
    })


@require_http_methods(["GET"])
def get_available_gateways_ajax(request):
    """Get available payment gateways via AJAX."""
    gateways = PaymentService.get_active_gateways()
    
    gateways_data = []
    for gateway in gateways:
        gateways_data.append({
            'id': str(gateway.id),
            'name': gateway.name,
            'title': gateway.title,
            'logo': gateway.logo.url if gateway.logo else None,
            'description': gateway.description,
            'gateway_type': gateway.gateway_type,
        })
    
    return JsonResponse({
        'success': True,
        'gateways': gateways_data
    })


@login_required
@require_http_methods(["POST"])
def create_transaction_ajax(request):
    """Create transaction via AJAX."""
    order_id = request.POST.get('order_id')
    gateway_type = request.POST.get('gateway_type')
    
    if not order_id or not gateway_type:
        return JsonResponse({'success': False, 'message': 'Order ID and gateway type are required'}, status=400)
    
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    # Create transaction
    transaction, result = PaymentService.create_payment(
        order=order,
        user=request.user,
        gateway_type=gateway_type,
        amount=order.total_amount,
        currency='IRR',
        description=f'پرداخت سفارش #{order.code}'
    )
    
    if not result['success']:
        return JsonResponse({'success': False, 'message': result.get('message')})
    
    return JsonResponse({
        'success': True,
        'transaction_id': str(transaction.id),
        'transaction_id_display': transaction.transaction_id,
    })
