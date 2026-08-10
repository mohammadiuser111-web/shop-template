"""
Views for accounts app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import random
import string
from datetime import timedelta
from django.utils import timezone

from .models import User, UserAddress, UserWishlist, OTP
from .forms import (
    LoginForm, RegistrationForm, OTPLoginForm, OTPVerifyForm,
    ProfileForm, UserAddressForm, PasswordChangeCustomForm,
    PasswordResetCustomForm, SetPasswordCustomForm
)
from apps.products.models import Product
from apps.orders.models import Order


# Authentication Views
@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, _('You have been logged in successfully.'))
                
                # Redirect to next or home
                next_url = request.GET.get('next') or request.POST.get('next')
                return redirect(next_url or 'store:home')
            else:
                messages.error(request, _('Invalid phone number/email or password.'))
    
    context = {
        'form': form,
        'title': _('Login'),
    }
    return render(request, 'accounts/login.html', context)


@require_http_methods(["POST"])
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, _('You have been logged out successfully.'))
    return redirect('store:home')


@require_http_methods(["GET", "POST"])
def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto login after registration
            login(request, user)
            messages.success(request, _('Your account has been created successfully!'))
            return redirect('store:home')
    
    context = {
        'form': form,
        'title': _('Register'),
    }
    return render(request, 'accounts/register.html', context)


# OTP Authentication Views
@require_http_methods(["GET", "POST"])
def phone_verification(request):
    """Phone verification for OTP login."""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    form = OTPLoginForm()
    if request.method == 'POST':
        form = OTPLoginForm(data=request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            
            # Generate OTP code
            otp_code = ''.join(random.choices(string.digits, k=6))
            
            # Get or create user
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'phone_number': phone_number,
                    'is_active': True,
                }
            )
            
            # Save OTP
            OTP.objects.create(
                user=user,
                code=otp_code,
                type='login',
                phone_number=phone_number,
                expires_at=timezone.now() + timedelta(minutes=5)
            )
            
            # In production, send SMS here
            # For now, just store in session for demo
            request.session['otp_phone'] = phone_number
            request.session['otp_code'] = otp_code
            
            messages.success(request, _('Verification code has been sent to your phone.'))
            return redirect('accounts:phone_verification_confirm')
    
    context = {
        'form': form,
        'title': _('Phone Verification'),
    }
    return render(request, 'accounts/phone_verification.html', context)


@require_http_methods(["GET", "POST"])
def phone_verification_confirm(request):
    """Confirm phone verification with OTP code."""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    form = OTPVerifyForm()
    if request.method == 'POST':
        form = OTPVerifyForm(data=request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            phone_number = request.session.get('otp_phone')
            
            # Check OTP
            try:
                otp = OTP.objects.filter(
                    phone_number=phone_number,
                    code=code,
                    type='login',
                    is_used=False
                ).order_by('-created_at').first()
                
                if otp and otp.is_valid():
                    otp.is_used = True
                    otp.save()
                    
                    # Login user
                    user = otp.user
                    login(request, user)
                    
                    # Clear session
                    request.session.pop('otp_phone', None)
                    request.session.pop('otp_code', None)
                    
                    messages.success(request, _('You have been logged in successfully.'))
                    return redirect('store:home')
                else:
                    messages.error(request, _('Invalid or expired verification code.'))
            except OTP.DoesNotExist:
                messages.error(request, _('Invalid verification code.'))
    
    context = {
        'form': form,
        'title': _('Verify Code'),
    }
    return render(request, 'accounts/phone_verification_confirm.html', context)


# Password Reset Views
@require_http_methods(["GET", "POST"])
def password_reset(request):
    """Password reset request view."""
    form = PasswordResetCustomForm()
    if request.method == 'POST':
        form = PasswordResetCustomForm(data=request.POST)
        if form.is_valid():
            # In a real implementation, send email with reset link
            messages.success(request, _('Password reset link has been sent to your email.'))
            return redirect('accounts:password_reset_done')
    
    context = {
        'form': form,
        'title': _('Password Reset'),
    }
    return render(request, 'accounts/password_reset.html', context)


def password_reset_done(request):
    """Password reset done view."""
    context = {
        'title': _('Password Reset Sent'),
    }
    return render(request, 'accounts/password_reset_done.html', context)


def password_reset_confirm(request, uidb64, token):
    """Password reset confirm view."""
    form = SetPasswordCustomForm(user=None)
    if request.method == 'POST':
        form = SetPasswordCustomForm(user=None, data=request.POST)
        if form.is_valid():
            # In a real implementation, update user password
            messages.success(request, _('Your password has been reset successfully!'))
            return redirect('accounts:password_reset_complete')
    
    context = {
        'form': form,
        'title': _('Set New Password'),
    }
    return render(request, 'accounts/password_reset_confirm.html', context)


def password_reset_complete(request):
    """Password reset complete view."""
    context = {
        'title': _('Password Reset Complete'),
    }
    return render(request, 'accounts/password_reset_complete.html', context)


# Profile Views
@login_required
def profile(request):
    """User profile view."""
    user = request.user
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Get wishlist
    wishlist_items = UserWishlist.objects.filter(user=user).select_related('product')[:10]
    
    context = {
        'user': user,
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
        'title': _('My Profile'),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    """Edit user profile."""
    user = request.user
    
    form = ProfileForm(instance=user)
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, files=request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated successfully!'))
            return redirect('accounts:profile')
    
    context = {
        'form': form,
        'title': _('Edit Profile'),
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def change_password(request):
    """Change user password."""
    form = PasswordChangeCustomForm(user=request.user)
    if request.method == 'POST':
        form = PasswordChangeCustomForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your password has been changed successfully!'))
            return redirect('accounts:profile')
    
    context = {
        'form': form,
        'title': _('Change Password'),
    }
    return render(request, 'accounts/change_password.html', context)


# Address Views
@login_required
def address_list(request):
    """List user addresses."""
    addresses = UserAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    context = {
        'addresses': addresses,
        'title': _('My Addresses'),
    }
    return render(request, 'accounts/address_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def address_add(request):
    """Add new address."""
    form = UserAddressForm(initial={'user': request.user})
    if request.method == 'POST':
        form = UserAddressForm(data=request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, _('Address has been added successfully!'))
            return redirect('accounts:address_list')
    
    context = {
        'form': form,
        'title': _('Add Address'),
    }
    return render(request, 'accounts/address_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def address_edit(request, pk):
    """Edit address."""
    address = get_object_or_404(UserAddress, pk=pk, user=request.user)
    
    form = UserAddressForm(instance=address)
    if request.method == 'POST':
        form = UserAddressForm(data=request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _('Address has been updated successfully!'))
            return redirect('accounts:address_list')
    
    context = {
        'form': form,
        'address': address,
        'title': _('Edit Address'),
    }
    return render(request, 'accounts/address_form.html', context)


@login_required
@require_http_methods(["POST"])
def address_delete(request, pk):
    """Delete address."""
    address = get_object_or_404(UserAddress, pk=pk, user=request.user)
    address.delete()
    messages.success(request, _('Address has been deleted successfully!'))
    return redirect('accounts:address_list')


@login_required
@require_http_methods(["POST"])
def set_default_address(request, pk):
    """Set address as default."""
    address = get_object_or_404(UserAddress, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, _('Default address has been set successfully!'))
    return redirect('accounts:address_list')


# Wishlist Views
@login_required
def wishlist(request):
    """User wishlist view."""
    wishlist_items = UserWishlist.objects.filter(user=request.user).select_related('product')
    
    # Pagination
    paginator = Paginator(wishlist_items, 12)
    page = request.GET.get('page')
    
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(1)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)
    
    context = {
        'items': items_page,
        'title': _('My Wishlist'),
    }
    return render(request, 'accounts/wishlist.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    # Check if already in wishlist
    existing = UserWishlist.objects.filter(user=request.user, product=product).exists()
    if existing:
        messages.warning(request, _('This product is already in your wishlist.'))
    else:
        UserWishlist.objects.create(user=request.user, product=product)
        messages.success(request, _('Product has been added to your wishlist!'))
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': not existing,
            'message': _('Added to wishlist') if not existing else _('Already in wishlist'),
            'wishlist_count': request.user.wishlist_items.count(),
        })
    
    return redirect('accounts:wishlist')


@login_required
@require_http_methods(["POST"])
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    product = get_object_or_404(Product, pk=product_id)
    
    wishlist_item = UserWishlist.objects.filter(user=request.user, product=product).first()
    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, _('Product has been removed from your wishlist!'))
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': _('Removed from wishlist'),
            'wishlist_count': request.user.wishlist_items.count(),
        })
    
    return redirect('accounts:wishlist')


# Order Views
@login_required
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
    return render(request, 'accounts/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Order detail view."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
        'title': _('Order #%(order_number)s') % {'order_number': order_number},
    }
    return render(request, 'accounts/order_detail.html', context)


@login_required
@require_http_methods(["POST"])
def order_cancel(request, order_number):
    """Cancel an order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if not order.can_be_cancelled():
        messages.error(request, _('This order cannot be cancelled.'))
        return redirect('accounts:order_detail', order_number=order_number)
    
    # Cancel the order
    order.status = 'cancelled'
    order.cancelled_at = timezone.now()
    order.save()
    
    messages.success(request, _('Your order has been cancelled successfully!'))
    return redirect('accounts:order_detail', order_number=order_number)


# AJAX Views
@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ajax_check_phone(request):
    """Check if phone number exists."""
    phone_number = request.POST.get('phone_number', '')
    exists = User.objects.filter(phone_number=phone_number).exists()
    return JsonResponse({'exists': exists})


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ajax_check_email(request):
    """Check if email exists."""
    email = request.POST.get('email', '')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})
