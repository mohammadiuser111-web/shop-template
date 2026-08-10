"""
Views for discounts app.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, Count
from django.utils import timezone

from .models import (
    Coupon, Discount, DiscountCategory, DiscountProduct,
    DiscountUsage, PriceRule
)
from .forms import (
    CouponForm, DiscountForm, PriceRuleForm,
    DiscountSearchForm
)
from apps.products.models import Product, Category, ProductVariant
from apps.cart.cart import Cart
from apps.orders.models import Order


def is_staff(user):
    """Check if user is staff."""
    return user.is_staff


# ==================== COUPONS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def coupon_list(request):
    """List all coupons."""
    # Filter by status
    status_filter = request.GET.get('status', 'active')
    search_query = request.GET.get('q')
    coupon_type = request.GET.get('type')
    
    coupons = Coupon.objects.all()
    
    if status_filter == 'active':
        coupons = coupons.filter(
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now()
        )
    elif status_filter == 'expired':
        coupons = coupons.filter(valid_until__lt=timezone.now())
    elif status_filter == 'inactive':
        coupons = coupons.filter(is_active=False)
    
    if search_query:
        coupons = coupons.filter(
            Q(code__icontains=search_query) | 
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if coupon_type:
        coupons = coupons.filter(discount_type=coupon_type)
    
    # Pagination
    paginator = Paginator(coupons, 20)
    page = request.GET.get('page')
    
    try:
        coupons_page = paginator.page(page)
    except PageNotAnInteger:
        coupons_page = paginator.page(1)
    except EmptyPage:
        coupons_page = paginator.page(paginator.num_pages)
    
    context = {
        'coupons': coupons_page,
        'current_status': status_filter,
        'current_type': coupon_type,
        'search_query': search_query,
        'title': _('Coupons'),
    }
    return render(request, 'discounts/coupon_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_coupon(request):
    """Create a new coupon."""
    if request.method == 'POST':
        form = CouponForm(data=request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.created_by = request.user
            coupon.save()
            
            # Add categories if provided
            categories = form.cleaned_data.get('categories')
            if categories:
                for category in categories:
                    DiscountCategory.objects.create(
                        coupon=coupon,
                        category=category
                    )
            
            # Add products if provided
            products = form.cleaned_data.get('products')
            if products:
                for product in products:
                    DiscountProduct.objects.create(
                        coupon=coupon,
                        product=product
                    )
            
            messages.success(request, _('Coupon created successfully.'))
            return redirect('discounts:coupon_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = CouponForm()
    
    context = {
        'form': form,
        'title': _('Create Coupon'),
    }
    return render(request, 'discounts/create_coupon.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_coupon(request, coupon_id):
    """Edit a coupon."""
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    
    if request.method == 'POST':
        form = CouponForm(data=request.POST, instance=coupon)
        if form.is_valid():
            coupon = form.save()
            
            # Update categories
            DiscountCategory.objects.filter(coupon=coupon).delete()
            categories = form.cleaned_data.get('categories')
            if categories:
                for category in categories:
                    DiscountCategory.objects.create(
                        coupon=coupon,
                        category=category
                    )
            
            # Update products
            DiscountProduct.objects.filter(coupon=coupon).delete()
            products = form.cleaned_data.get('products')
            if products:
                for product in products:
                    DiscountProduct.objects.create(
                        coupon=coupon,
                        product=product
                    )
            
            messages.success(request, _('Coupon updated.'))
            return redirect('discounts:coupon_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = CouponForm(instance=coupon)
    
    context = {
        'coupon': coupon,
        'form': form,
        'title': _('Edit Coupon'),
    }
    return render(request, 'discounts/edit_coupon.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_coupon(request, coupon_id):
    """Delete a coupon."""
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    
    # Check if coupon has been used
    if DiscountUsage.objects.filter(coupon=coupon).exists():
        messages.error(request, _('Cannot delete a coupon that has been used.'))
        return redirect('discounts:coupon_list')
    
    coupon.delete()
    messages.success(request, _('Coupon deleted.'))
    return redirect('discounts:coupon_list')


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def toggle_coupon_status(request, coupon_id):
    """Toggle coupon active status."""
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    
    coupon.is_active = not coupon.is_active
    coupon.save()
    
    messages.success(request, _('Coupon status updated.'))
    return redirect('discounts:coupon_list')


# ==================== DISCOUNTS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def discount_list(request):
    """List all discounts."""
    discounts = Discount.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status', 'active')
    search_query = request.GET.get('q')
    
    if status_filter == 'active':
        discounts = discounts.filter(
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now()
        )
    elif status_filter == 'expired':
        discounts = discounts.filter(valid_until__lt=timezone.now())
    elif status_filter == 'inactive':
        discounts = discounts.filter(is_active=False)
    
    if search_query:
        discounts = discounts.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(discounts, 20)
    page = request.GET.get('page')
    
    try:
        discounts_page = paginator.page(page)
    except PageNotAnInteger:
        discounts_page = paginator.page(1)
    except EmptyPage:
        discounts_page = paginator.page(paginator.num_pages)
    
    context = {
        'discounts': discounts_page,
        'current_status': status_filter,
        'search_query': search_query,
        'title': _('Discounts'),
    }
    return render(request, 'discounts/discount_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_discount(request):
    """Create a new discount."""
    if request.method == 'POST':
        form = DiscountForm(data=request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.created_by = request.user
            discount.save()
            
            messages.success(request, _('Discount created successfully.'))
            return redirect('discounts:discount_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = DiscountForm()
    
    context = {
        'form': form,
        'title': _('Create Discount'),
    }
    return render(request, 'discounts/create_discount.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_discount(request, discount_id):
    """Edit a discount."""
    discount = get_object_or_404(Discount, pk=discount_id)
    
    if request.method == 'POST':
        form = DiscountForm(data=request.POST, instance=discount)
        if form.is_valid():
            discount = form.save()
            messages.success(request, _('Discount updated.'))
            return redirect('discounts:discount_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = DiscountForm(instance=discount)
    
    context = {
        'discount': discount,
        'form': form,
        'title': _('Edit Discount'),
    }
    return render(request, 'discounts/edit_discount.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_discount(request, discount_id):
    """Delete a discount."""
    discount = get_object_or_404(Discount, pk=discount_id)
    discount.delete()
    messages.success(request, _('Discount deleted.'))
    return redirect('discounts:discount_list')


# ==================== PRICE RULES ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def price_rule_list(request):
    """List all price rules."""
    rules = PriceRule.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status', 'active')
    search_query = request.GET.get('q')
    
    if status_filter == 'active':
        rules = rules.filter(is_active=True)
    elif status_filter == 'inactive':
        rules = rules.filter(is_active=False)
    
    if search_query:
        rules = rules.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(rules, 20)
    page = request.GET.get('page')
    
    try:
        rules_page = paginator.page(page)
    except PageNotAnInteger:
        rules_page = paginator.page(1)
    except EmptyPage:
        rules_page = paginator.page(paginator.num_pages)
    
    context = {
        'rules': rules_page,
        'current_status': status_filter,
        'search_query': search_query,
        'title': _('Price Rules'),
    }
    return render(request, 'discounts/price_rule_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_price_rule(request):
    """Create a new price rule."""
    if request.method == 'POST':
        form = PriceRuleForm(data=request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.created_by = request.user
            rule.save()
            
            messages.success(request, _('Price rule created successfully.'))
            return redirect('discounts:price_rule_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = PriceRuleForm()
    
    context = {
        'form': form,
        'title': _('Create Price Rule'),
    }
    return render(request, 'discounts/create_price_rule.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_price_rule(request, rule_id):
    """Edit a price rule."""
    rule = get_object_or_404(PriceRule, pk=rule_id)
    
    if request.method == 'POST':
        form = PriceRuleForm(data=request.POST, instance=rule)
        if form.is_valid():
            rule = form.save()
            messages.success(request, _('Price rule updated.'))
            return redirect('discounts:price_rule_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = PriceRuleForm(instance=rule)
    
    context = {
        'rule': rule,
        'form': form,
        'title': _('Edit Price Rule'),
    }
    return render(request, 'discounts/edit_price_rule.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_price_rule(request, rule_id):
    """Delete a price rule."""
    rule = get_object_or_404(PriceRule, pk=rule_id)
    rule.delete()
    messages.success(request, _('Price rule deleted.'))
    return redirect('discounts:price_rule_list')


# ==================== COUPON VALIDATION ====================

@require_http_methods(["POST"])
@csrf_exempt
def validate_coupon(request):
    """Validate a coupon code via AJAX."""
    code = request.POST.get('code')
    cart_total = float(request.POST.get('cart_total', 0))
    user_id = request.POST.get('user_id')
    
    if not code:
        return JsonResponse({'valid': False, 'error': 'Coupon code is required'}, status=400)
    
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'Invalid coupon code'})
    
    # Check if coupon is valid
    now = timezone.now()
    if coupon.valid_from and coupon.valid_from > now:
        return JsonResponse({'valid': False, 'error': 'Coupon is not yet valid'})
    
    if coupon.valid_until and coupon.valid_until < now:
        return JsonResponse({'valid': False, 'error': 'Coupon has expired'})
    
    # Check minimum cart value
    if coupon.min_cart_value and cart_total < coupon.min_cart_value:
        return JsonResponse({
            'valid': False,
            'error': f'Minimum cart value of ${coupon.min_cart_value} required'
        })
    
    # Check if user can use this coupon
    if user_id:
        user = get_object_or_404(User, pk=user_id)
        
        # Check if coupon is user-specific
        if coupon.user and coupon.user != user:
            return JsonResponse({'valid': False, 'error': 'This coupon is not valid for your account'})
        
        # Check if user has already used this coupon
        if coupon.max_uses_per_user:
            usage_count = DiscountUsage.objects.filter(
                coupon=coupon,
                user=user
            ).count()
            if usage_count >= coupon.max_uses_per_user:
                return JsonResponse({'valid': False, 'error': 'You have already used this coupon'})
    
    # Check total usage
    if coupon.max_uses:
        total_usage = DiscountUsage.objects.filter(coupon=coupon).count()
        if total_usage >= coupon.max_uses:
            return JsonResponse({'valid': False, 'error': 'Coupon has reached maximum usage limit'})
    
    # Calculate discount amount
    discount_amount = 0
    if coupon.discount_type == 'percentage':
        discount_amount = cart_total * (coupon.discount_value / 100)
    elif coupon.discount_type == 'fixed':
        discount_amount = coupon.discount_value
    
    # Check maximum discount
    if coupon.max_discount and discount_amount > coupon.max_discount:
        discount_amount = coupon.max_discount
    
    return JsonResponse({
        'valid': True,
        'coupon': {
            'id': str(coupon.id),
            'code': coupon.code,
            'name': coupon.name,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'discount_amount': discount_amount,
            'min_cart_value': coupon.min_cart_value,
            'max_discount': coupon.max_discount,
        },
        'discount_amount': discount_amount,
        'new_total': cart_total - discount_amount,
    })


@require_http_methods(["POST"])
@csrf_exempt
def apply_coupon(request):
    """Apply a coupon to the cart."""
    code = request.POST.get('code')
    
    if not code:
        return JsonResponse({'success': False, 'error': 'Coupon code is required'}, status=400)
    
    # Validate coupon
    response = validate_coupon(request)
    response_data = json.loads(response.content)
    
    if not response_data.get('valid'):
        return JsonResponse({
            'success': False,
            'error': response_data.get('error', 'Invalid coupon')
        })
    
    # In a real implementation, save coupon to session/cart
    # For now, just return success
    return JsonResponse({
        'success': True,
        'coupon': response_data.get('coupon'),
        'discount_amount': response_data.get('discount_amount'),
    })


@require_http_methods(["POST"])
@csrf_exempt
def remove_coupon(request):
    """Remove a coupon from the cart."""
    # In a real implementation, remove coupon from session/cart
    return JsonResponse({'success': True})


# ==================== DISCOUNT DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def discount_dashboard(request):
    """Discount dashboard."""
    # Get counts
    total_coupons = Coupon.objects.count()
    active_coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    ).count()
    total_discounts = Discount.objects.count()
    active_discounts = Discount.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    ).count()
    
    # Get recent coupons
    recent_coupons = Coupon.objects.order_by('-created_at')[:5]
    
    # Get most used coupons
    most_used_coupons = DiscountUsage.objects.values('coupon__code', 'coupon__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Get usage statistics
    total_usage = DiscountUsage.objects.count()
    total_discount_value = DiscountUsage.objects.aggregate(
        total=Sum('discount_amount')
    )['total'] or 0
    
    context = {
        'total_coupons': total_coupons,
        'active_coupons': active_coupons,
        'total_discounts': total_discounts,
        'active_discounts': active_discounts,
        'recent_coupons': recent_coupons,
        'most_used_coupons': most_used_coupons,
        'total_usage': total_usage,
        'total_discount_value': total_discount_value,
        'title': _('Discount Dashboard'),
    }
    return render(request, 'discounts/discount_dashboard.html', context)


# ==================== COUPON USAGE ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def coupon_usage(request, coupon_id):
    """List coupon usage history."""
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    
    usages = DiscountUsage.objects.filter(
        coupon=coupon
    ).select_related('user', 'order').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(usages, 20)
    page = request.GET.get('page')
    
    try:
        usages_page = paginator.page(page)
    except PageNotAnInteger:
        usages_page = paginator.page(1)
    except EmptyPage:
        usages_page = paginator.page(paginator.num_pages)
    
    context = {
        'coupon': coupon,
        'usages': usages_page,
        'title': f"{_('Usage History for')} {coupon.code}",
    }
    return render(request, 'discounts/coupon_usage.html', context)


# ==================== AJAX VIEWS ====================

@require_http_methods(["GET"])
def get_active_coupons_ajax(request):
    """Get active coupons via AJAX."""
    coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    )
    
    coupons_data = []
    for coupon in coupons:
        coupons_data.append({
            'id': str(coupon.id),
            'code': coupon.code,
            'name': coupon.name,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'min_cart_value': coupon.min_cart_value,
            'valid_until': coupon.valid_until.strftime('%Y-%m-%d') if coupon.valid_until else None,
        })
    
    return JsonResponse({'coupons': coupons_data})


@require_http_methods(["GET"])
def get_coupon_details_ajax(request, coupon_id):
    """Get coupon details via AJAX."""
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    
    return JsonResponse({
        'id': str(coupon.id),
        'code': coupon.code,
        'name': coupon.name,
        'description': coupon.description,
        'discount_type': coupon.discount_type,
        'discount_value': coupon.discount_value,
        'min_cart_value': coupon.min_cart_value,
        'max_discount': coupon.max_discount,
        'max_uses': coupon.max_uses,
        'max_uses_per_user': coupon.max_uses_per_user,
        'is_active': coupon.is_active,
        'valid_from': coupon.valid_from.strftime('%Y-%m-%d %H:%M:%S') if coupon.valid_from else None,
        'valid_until': coupon.valid_until.strftime('%Y-%m-%d %H:%M:%S') if coupon.valid_until else None,
        'usage_count': DiscountUsage.objects.filter(coupon=coupon).count(),
    })


@require_http_methods(["GET"])
def get_discount_summary_ajax(request):
    """Get discount summary via AJAX."""
    total_coupons = Coupon.objects.count()
    active_coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    ).count()
    
    total_discounts = Discount.objects.count()
    active_discounts = Discount.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    ).count()
    
    total_usage = DiscountUsage.objects.count()
    
    return JsonResponse({
        'total_coupons': total_coupons,
        'active_coupons': active_coupons,
        'total_discounts': total_discounts,
        'active_discounts': active_discounts,
        'total_usage': total_usage,
    })


@require_http_methods(["GET"])
def check_coupon_eligibility_ajax(request):
    """Check if products in cart are eligible for coupon."""
    code = request.GET.get('code')
    product_ids = request.GET.getlist('product_ids[]')
    
    if not code or not product_ids:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Invalid coupon code'})
    
    # Check if products are eligible
    eligible = True
    ineligible_products = []
    
    for product_id in product_ids:
        product = get_object_or_404(Product, pk=product_id)
        
        # Check if coupon applies to specific categories
        if coupon.categories.exists():
            if not product.categories.filter(id__in=coupon.categories.values_list('category__id', flat=True)).exists():
                ineligible_products.append(product.name)
                eligible = False
        
        # Check if coupon applies to specific products
        if coupon.products.exists():
            if not coupon.products.filter(product=product).exists():
                ineligible_products.append(product.name)
                eligible = False
        
        # Check if product is excluded
        if coupon.excluded_products.exists():
            if coupon.excluded_products.filter(product=product).exists():
                ineligible_products.append(product.name)
                eligible = False
        
        # Check if product category is excluded
        if coupon.excluded_categories.exists():
            if product.categories.filter(id__in=coupon.excluded_categories.values_list('category__id', flat=True)).exists():
                ineligible_products.append(product.name)
                eligible = False
    
    return JsonResponse({
        'eligible': eligible,
        'ineligible_products': ineligible_products,
    })
