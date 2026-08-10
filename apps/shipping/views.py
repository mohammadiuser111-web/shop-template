"""
Views for shipping app.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, F, DecimalField
from django.db.models.functions import Coalesce

from .models import (
    ShippingZone, ShippingMethod, ShippingRule, ShippingClass,
    PickupLocation, DeliveryTime, ShippingRate, Package
)
from .forms import (
    ShippingAddressForm, PickupLocationForm,
    ShippingCalculatorForm
)
from apps.accounts.models import UserAddress
from apps.products.models import Product, CartItem
from apps.cart.cart import Cart
from apps.orders.models import Order


# ==================== SHIPPING CALCULATOR ====================

@require_http_methods(["GET", "POST"])
def shipping_calculator(request):
    """Shipping cost calculator."""
    cart = Cart(request)
    
    if request.method == 'POST':
        form = ShippingCalculatorForm(data=request.POST)
        if form.is_valid():
            country = form.cleaned_data.get('country')
            state = form.cleaned_data.get('state')
            city = form.cleaned_data.get('city')
            postal_code = form.cleaned_data.get('postal_code')
            
            # Calculate shipping cost
            shipping_cost, methods = calculate_shipping(
                cart=cart,
                country=country,
                state=state,
                city=city,
                postal_code=postal_code
            )
            
            context = {
                'form': form,
                'shipping_cost': shipping_cost,
                'methods': methods,
                'title': _('Shipping Calculator'),
            }
            return render(request, 'shipping/shipping_calculator.html', context)
    else:
        form = ShippingCalculatorForm()
    
    context = {
        'form': form,
        'title': _('Shipping Calculator'),
    }
    return render(request, 'shipping/shipping_calculator.html', context)


def calculate_shipping(cart, country, state=None, city=None, postal_code=None):
    """Calculate shipping cost based on cart and destination."""
    # Get all items and their shipping classes
    items = []
    total_weight = 0
    total_value = 0
    
    for item in cart:
        product = item['product']
        items.append({
            'product': product,
            'quantity': item['quantity'],
            'weight': product.weight if product.weight else 0,
            'value': product.price * item['quantity'],
            'shipping_class': product.shipping_class,
        })
        total_weight += (product.weight if product.weight else 0) * item['quantity']
        total_value += product.price * item['quantity']
    
    # Find matching shipping zone
    zone = ShippingZone.objects.filter(
        is_active=True,
        countries__code=country
    ).first()
    
    if not zone:
        # Try to find a zone with states
        zone = ShippingZone.objects.filter(
            is_active=True,
            states__code=state
        ).first()
    
    if not zone:
        # Try to find a zone with postal codes
        zone = ShippingZone.objects.filter(
            is_active=True,
            postal_codes__code=postal_code
        ).first()
    
    if not zone:
        # Default zone
        zone = ShippingZone.objects.filter(
            is_active=True,
            is_default=True
        ).first()
    
    if not zone:
        return 0, []
    
    # Get available methods for this zone
    methods = ShippingMethod.objects.filter(
        zones=zone,
        is_active=True
    ).prefetch_related('rules')
    
    available_methods = []
    
    for method in methods:
        # Check rules
        is_valid = True
        cost = method.base_cost
        
        for rule in method.rules.all():
            if rule.type == 'min_weight' and total_weight < rule.value:
                is_valid = False
                break
            elif rule.type == 'max_weight' and total_weight > rule.value:
                is_valid = False
                break
            elif rule.type == 'min_value' and total_value < rule.value:
                is_valid = False
                break
            elif rule.type == 'max_value' and total_value > rule.value:
                is_valid = False
                break
            elif rule.type == 'add_cost':
                cost += rule.value
            elif rule.type == 'multiply_cost':
                cost *= rule.value
        
        if is_valid:
            available_methods.append({
                'id': method.id,
                'name': method.name,
                'description': method.description,
                'cost': cost,
                'estimated_delivery': method.estimated_delivery,
                'icon': method.icon.url if method.icon else None,
            })
    
    # Sort by cost
    available_methods.sort(key=lambda x: x['cost'])
    
    # Return total cost for cheapest method
    if available_methods:
        return available_methods[0]['cost'], available_methods
    
    return 0, []


# ==================== SHIPPING METHODS ====================

@require_http_methods(["GET"])
def shipping_methods(request):
    """List available shipping methods."""
    country = request.GET.get('country')
    state = request.GET.get('state')
    city = request.GET.get('city')
    
    zones = ShippingZone.objects.filter(is_active=True)
    
    if country:
        zones = zones.filter(Q(countries__code=country) | Q(is_default=True))
    
    methods = ShippingMethod.objects.filter(
        zones__in=zones,
        is_active=True
    ).distinct().prefetch_related('zones', 'rules')
    
    context = {
        'methods': methods,
        'country': country,
        'state': state,
        'city': city,
        'title': _('Shipping Methods'),
    }
    return render(request, 'shipping/shipping_methods.html', context)


@require_http_methods(["GET"])
def shipping_method_detail(request, slug):
    """Shipping method detail."""
    method = get_object_or_404(ShippingMethod, slug=slug, is_active=True)
    
    zones = method.zones.filter(is_active=True)
    
    context = {
        'method': method,
        'zones': zones,
        'title': method.name,
        'meta_title': method.meta_title or method.name,
        'meta_description': method.meta_description or method.description,
    }
    return render(request, 'shipping/shipping_method_detail.html', context)


# ==================== PICKUP LOCATIONS ====================

@require_http_methods(["GET"])
def pickup_locations(request):
    """List pickup locations."""
    locations = PickupLocation.objects.filter(is_active=True)
    
    # Filter by search
    query = request.GET.get('q')
    if query:
        locations = locations.filter(
            Q(name__icontains=query) | 
            Q(address__icontains=query) | 
            Q(city__icontains=query) | 
            Q(postal_code__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(locations, 20)
    page = request.GET.get('page')
    
    try:
        locations_page = paginator.page(page)
    except PageNotAnInteger:
        locations_page = paginator.page(1)
    except EmptyPage:
        locations_page = paginator.page(paginator.num_pages)
    
    context = {
        'locations': locations_page,
        'query': query,
        'title': _('Pickup Locations'),
    }
    return render(request, 'shipping/pickup_locations.html', context)


@require_http_methods(["GET"])
def pickup_location_detail(request, slug):
    """Pickup location detail."""
    location = get_object_or_404(PickupLocation, slug=slug, is_active=True)
    
    # Get opening hours
    opening_hours = location.get_opening_hours()
    
    # Get map URL
    map_url = location.get_map_url()
    
    context = {
        'location': location,
        'opening_hours': opening_hours,
        'map_url': map_url,
        'title': location.name,
        'meta_title': location.meta_title or location.name,
        'meta_description': location.meta_description or location.address,
    }
    return render(request, 'shipping/pickup_location_detail.html', context)


# ==================== SHIPPING CLASSES ====================

@require_http_methods(["GET"])
def shipping_classes(request):
    """List shipping classes."""
    classes = ShippingClass.objects.filter(is_active=True)
    
    context = {
        'classes': classes,
        'title': _('Shipping Classes'),
    }
    return render(request, 'shipping/shipping_classes.html', context)


# ==================== DELIVERY TIME ====================

@require_http_methods(["GET"])
def delivery_time(request):
    """Estimated delivery time page."""
    delivery_times = DeliveryTime.objects.filter(is_active=True)
    
    context = {
        'delivery_times': delivery_times,
        'title': _('Delivery Time Estimates'),
    }
    return render(request, 'shipping/delivery_time.html', context)


# ==================== SHIPPING POLICY ====================

@require_http_methods(["GET"])
def shipping_policy(request):
    """Shipping policy page."""
    context = {
        'title': _('Shipping Policy'),
    }
    return render(request, 'shipping/shipping_policy.html', context)


# ==================== RETURNS POLICY ====================

@require_http_methods(["GET"])
def returns_policy(request):
    """Returns policy page."""
    context = {
        'title': _('Returns Policy'),
    }
    return render(request, 'shipping/returns_policy.html', context)


# ==================== TRACK ORDER ====================

@require_http_methods(["GET", "POST"])
def track_order(request):
    """Track order shipping status."""
    tracking_number = request.GET.get('tracking_number')
    order_id = request.GET.get('order_id')
    
    order = None
    tracking_info = None
    
    if order_id:
        order = get_object_or_404(Order, pk=order_id)
        if order.user != request.user and not request.user.is_staff:
            order = None
    
    if tracking_number:
        # In a real implementation, integrate with shipping carrier API
        # For demo, simulate tracking info
        tracking_info = {
            'tracking_number': tracking_number,
            'carrier': 'FedEx',
            'status': 'In Transit',
            'estimated_delivery': '2026-08-15',
            'history': [
                {
                    'date': '2026-08-10',
                    'time': '10:00 AM',
                    'location': 'Dallas, TX',
                    'status': 'Package received',
                },
                {
                    'date': '2026-08-10',
                    'time': '12:00 PM',
                    'location': 'Dallas, TX',
                    'status': 'In transit',
                },
            ]
        }
    
    context = {
        'order': order,
        'tracking_number': tracking_number,
        'tracking_info': tracking_info,
        'title': _('Track Order'),
    }
    return render(request, 'shipping/track_order.html', context)


@require_http_methods(["GET"])
def get_tracking_info_ajax(request):
    """Get tracking info via AJAX."""
    tracking_number = request.GET.get('tracking_number')
    
    if not tracking_number:
        return JsonResponse({'error': 'Tracking number required'}, status=400)
    
    # In a real implementation, call carrier API
    # For demo, return simulated data
    tracking_info = {
        'tracking_number': tracking_number,
        'carrier': 'FedEx',
        'status': 'In Transit',
        'estimated_delivery': '2026-08-15',
        'history': [
            {
                'date': '2026-08-10',
                'time': '10:00 AM',
                'location': 'Dallas, TX',
                'status': 'Package received',
            },
        ]
    }
    
    return JsonResponse({'tracking_info': tracking_info})


# ==================== SHIPPING ADDRESS ====================

@login_required
@require_http_methods(["GET", "POST"])
def shipping_address(request):
    """Manage shipping addresses."""
    addresses = UserAddress.objects.filter(
        user=request.user,
        address_type='shipping'
    )
    
    if request.method == 'POST':
        form = ShippingAddressForm(data=request.POST)
        if form.is_valid():
            address = UserAddress.objects.create(
                user=request.user,
                address_type='shipping',
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                company=form.cleaned_data.get('company'),
                phone=form.cleaned_data.get('phone'),
                email=form.cleaned_data.get('email'),
                country=form.cleaned_data.get('country'),
                state=form.cleaned_data.get('state'),
                city=form.cleaned_data.get('city'),
                address_line_1=form.cleaned_data.get('address_line_1'),
                address_line_2=form.cleaned_data.get('address_line_2'),
                postal_code=form.cleaned_data.get('postal_code'),
                is_default=form.cleaned_data.get('is_default'),
            )
            
            # If this is the first address, make it default
            if not addresses.exists():
                address.is_default = True
                address.save()
            
            messages.success(request, _('Shipping address added successfully.'))
            return redirect('shipping:shipping_address')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ShippingAddressForm()
    
    context = {
        'addresses': addresses,
        'form': form,
        'title': _('Shipping Addresses'),
    }
    return render(request, 'shipping/shipping_address.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_shipping_address(request, address_id):
    """Edit shipping address."""
    address = get_object_or_404(UserAddress, pk=address_id, user=request.user, address_type='shipping')
    
    if request.method == 'POST':
        form = ShippingAddressForm(data=request.POST, instance=address)
        if form.is_valid():
            address = form.save()
            messages.success(request, _('Shipping address updated.'))
            return redirect('shipping:shipping_address')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ShippingAddressForm(instance=address)
    
    context = {
        'address': address,
        'form': form,
        'title': _('Edit Shipping Address'),
    }
    return render(request, 'shipping/edit_shipping_address.html', context)


@login_required
@require_http_methods(["POST"])
def delete_shipping_address(request, address_id):
    """Delete shipping address."""
    address = get_object_or_404(UserAddress, pk=address_id, user=request.user, address_type='shipping')
    
    address.delete()
    messages.success(request, _('Shipping address deleted.'))
    return redirect('shipping:shipping_address')


@login_required
@require_http_methods(["POST"])
def set_default_shipping_address(request, address_id):
    """Set default shipping address."""
    address = get_object_or_404(UserAddress, pk=address_id, user=request.user, address_type='shipping')
    
    # Clear default from all other addresses
    UserAddress.objects.filter(
        user=request.user,
        address_type='shipping'
    ).update(is_default=False)
    
    # Set this as default
    address.is_default = True
    address.save()
    
    messages.success(request, _('Default shipping address updated.'))
    return redirect('shipping:shipping_address')


# ==================== AJAX VIEWS ====================

@require_http_methods(["GET"])
def get_shipping_cost_ajax(request):
    """Get shipping cost via AJAX."""
    country = request.GET.get('country')
    state = request.GET.get('state')
    city = request.GET.get('city')
    postal_code = request.GET.get('postal_code')
    cart_items = request.GET.get('cart_items')
    
    if not country:
        return JsonResponse({'error': 'Country is required'}, status=400)
    
    # Parse cart items
    items = []
    if cart_items:
        try:
            items = json.loads(cart_items)
        except json.JSONDecodeError:
            pass
    
    # Calculate shipping
    cart = Cart(request)
    shipping_cost, methods = calculate_shipping(
        cart=cart,
        country=country,
        state=state,
        city=city,
        postal_code=postal_code
    )
    
    methods_data = []
    for method in methods:
        methods_data.append({
            'id': method['id'],
            'name': method['name'],
            'description': method['description'],
            'cost': method['cost'],
            'estimated_delivery': method['estimated_delivery'],
            'icon': method['icon'],
        })
    
    return JsonResponse({
        'shipping_cost': shipping_cost,
        'methods': methods_data,
    })


@require_http_methods(["GET"])
def get_shipping_methods_ajax(request):
    """Get available shipping methods via AJAX."""
    country = request.GET.get('country')
    state = request.GET.get('state')
    city = request.GET.get('city')
    postal_code = request.GET.get('postal_code')
    
    zones = ShippingZone.objects.filter(is_active=True)
    
    if country:
        zones = zones.filter(Q(countries__code=country) | Q(is_default=True))
    
    methods = ShippingMethod.objects.filter(
        zones__in=zones,
        is_active=True
    ).distinct()
    
    methods_data = []
    for method in methods:
        methods_data.append({
            'id': str(method.id),
            'name': method.name,
            'description': method.description,
            'base_cost': method.base_cost,
            'estimated_delivery': method.estimated_delivery,
            'icon': method.icon.url if method.icon else None,
        })
    
    return JsonResponse({'methods': methods_data})


@require_http_methods(["GET"])
def get_pickup_locations_ajax(request):
    """Get pickup locations via AJAX."""
    query = request.GET.get('q', '')
    
    locations = PickupLocation.objects.filter(
        is_active=True,
        Q(name__icontains=query) | 
        Q(address__icontains=query) | 
        Q(city__icontains=query)
    )[:10]
    
    locations_data = []
    for location in locations:
        locations_data.append({
            'id': str(location.id),
            'name': location.name,
            'address': location.address,
            'city': location.city,
            'postal_code': location.postal_code,
            'phone': location.phone,
            'latitude': location.latitude,
            'longitude': location.longitude,
        })
    
    return JsonResponse({'locations': locations_data})


@require_http_methods(["GET"])
def get_delivery_estimate_ajax(request):
    """Get delivery time estimate via AJAX."""
    method_id = request.GET.get('method_id')
    country = request.GET.get('country')
    state = request.GET.get('state')
    city = request.GET.get('city')
    
    if not method_id:
        return JsonResponse({'error': 'Method ID is required'}, status=400)
    
    method = get_object_or_404(ShippingMethod, pk=method_id)
    
    # Get zone
    zone = ShippingZone.objects.filter(
        is_active=True,
        countries__code=country
    ).first()
    
    if not zone:
        zone = ShippingZone.objects.filter(
            is_active=True,
            is_default=True
        ).first()
    
    # Check if method is available for this zone
    if zone and method.zones.filter(pk=zone.pk).exists():
        estimated_delivery = method.estimated_delivery
    else:
        estimated_delivery = '5-7 business days'
    
    return JsonResponse({
        'estimated_delivery': estimated_delivery,
        'min_days': method.min_days if hasattr(method, 'min_days') else None,
        'max_days': method.max_days if hasattr(method, 'max_days') else None,
    })
