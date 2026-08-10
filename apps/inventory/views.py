"""
Views for inventory app.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, Count, F
from django.utils import timezone

from .models import (
    Stock, StockMovement, StockLocation, StockStatus,
    LowStockAlert, InventoryReport, Supplier, PurchaseOrder,
    PurchaseOrderItem, Warehouse
)
from .forms import (
    StockAdjustmentForm, StockTransferForm, StockSearchForm,
    SupplierForm, PurchaseOrderForm, WarehouseForm,
    LowStockAlertForm
)
from apps.products.models import Product, ProductVariant
from apps.accounts.models import User


def is_staff(user):
    """Check if user is staff."""
    return user.is_staff


# ==================== STOCK MANAGEMENT ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def stock_list(request):
    """List all stock items."""
    # Filter by product
    product_id = request.GET.get('product')
    variant_id = request.GET.get('variant')
    location_id = request.GET.get('location')
    status = request.GET.get('status')
    search_query = request.GET.get('q')
    low_stock = request.GET.get('low_stock')
    
    stocks = Stock.objects.filter(
        product_variant__is_active=True
    ).select_related(
        'product_variant__product',
        'location'
    ).order_by('-updated_at')
    
    if product_id:
        stocks = stocks.filter(product_variant__product__id=product_id)
    
    if variant_id:
        stocks = stocks.filter(product_variant__id=variant_id)
    
    if location_id:
        stocks = stocks.filter(location__id=location_id)
    
    if status:
        stocks = stocks.filter(status=status)
    
    if search_query:
        stocks = stocks.filter(
            Q(product_variant__product__name__icontains=search_query) | 
            Q(product_variant__sku__icontains=search_query) | 
            Q(product_variant__product__sku__icontains=search_query) | 
            Q(location__name__icontains=search_query)
        )
    
    if low_stock:
        stocks = stocks.filter(quantity__lte=F('product_variant__low_stock_threshold'))
    
    # Pagination
    paginator = Paginator(stocks, 20)
    page = request.GET.get('page')
    
    try:
        stocks_page = paginator.page(page)
    except PageNotAnInteger:
        stocks_page = paginator.page(1)
    except EmptyPage:
        stocks_page = paginator.page(paginator.num_pages)
    
    locations = StockLocation.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)[:100]
    statuses = StockStatus.objects.all()
    
    context = {
        'stocks': stocks_page,
        'locations': locations,
        'products': products,
        'statuses': statuses,
        'current_product': product_id,
        'current_variant': variant_id,
        'current_location': location_id,
        'current_status': status,
        'search_query': search_query,
        'low_stock': low_stock,
        'title': _('Stock List'),
    }
    return render(request, 'inventory/stock_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def stock_detail(request, stock_id):
    """Stock item detail."""
    stock = get_object_or_404(Stock, pk=stock_id)
    
    # Get movement history
    movements = StockMovement.objects.filter(
        stock=stock
    ).select_related('user', 'related_order').order_by('-created_at')[:20]
    
    # Get low stock alerts
    alerts = LowStockAlert.objects.filter(
        stock=stock
    ).order_by('-created_at')[:10]
    
    context = {
        'stock': stock,
        'movements': movements,
        'alerts': alerts,
        'title': f"{_('Stock Detail for')} {stock.product_variant}",
    }
    return render(request, 'inventory/stock_detail.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def stock_adjustment(request):
    """Adjust stock quantity."""
    if request.method == 'POST':
        form = StockAdjustmentForm(data=request.POST)
        if form.is_valid():
            stock = form.cleaned_data.get('stock')
            adjustment_type = form.cleaned_data.get('adjustment_type')
            quantity = form.cleaned_data.get('quantity')
            reason = form.cleaned_data.get('reason')
            
            # Calculate new quantity
            if adjustment_type == 'add':
                new_quantity = stock.quantity + quantity
            elif adjustment_type == 'subtract':
                new_quantity = stock.quantity - quantity
            else:
                new_quantity = quantity
            
            # Update stock
            stock.quantity = new_quantity
            stock.save()
            
            # Create movement record
            StockMovement.objects.create(
                stock=stock,
                movement_type=adjustment_type,
                quantity=quantity,
                previous_quantity=stock.quantity - quantity if adjustment_type != 'set' else stock.quantity,
                new_quantity=new_quantity,
                user=request.user,
                reason=reason,
                notes=form.cleaned_data.get('notes'),
            )
            
            # Check for low stock
            if new_quantity <= stock.product_variant.low_stock_threshold:
                LowStockAlert.objects.create(
                    stock=stock,
                    current_quantity=new_quantity,
                    threshold=stock.product_variant.low_stock_threshold,
                    is_resolved=False,
                )
            
            messages.success(request, _('Stock adjusted successfully.'))
            return redirect('inventory:stock_detail', stock_id=stock.pk)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = StockAdjustmentForm()
    
    context = {
        'form': form,
        'title': _('Stock Adjustment'),
    }
    return render(request, 'inventory/stock_adjustment.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def stock_transfer(request):
    """Transfer stock between locations."""
    if request.method == 'POST':
        form = StockTransferForm(data=request.POST)
        if form.is_valid():
            source_stock = form.cleaned_data.get('source_stock')
            destination_location = form.cleaned_data.get('destination_location')
            quantity = form.cleaned_data.get('quantity')
            reason = form.cleaned_data.get('reason')
            
            # Check if source has enough stock
            if source_stock.quantity < quantity:
                messages.error(request, _('Source location does not have enough stock.'))
                return redirect('inventory:stock_transfer')
            
            # Get or create destination stock
            destination_stock, created = Stock.objects.get_or_create(
                product_variant=source_stock.product_variant,
                location=destination_location,
                defaults={
                    'quantity': 0,
                    'status': 'in_stock',
                }
            )
            
            # Update source stock
            source_stock.quantity -= quantity
            source_stock.save()
            
            # Update destination stock
            destination_stock.quantity += quantity
            destination_stock.save()
            
            # Create movement records
            StockMovement.objects.create(
                stock=source_stock,
                movement_type='transfer_out',
                quantity=quantity,
                previous_quantity=source_stock.quantity + quantity,
                new_quantity=source_stock.quantity,
                user=request.user,
                reason=reason,
                related_movement_type='stock_transfer',
                related_movement_id=destination_stock.pk,
            )
            
            StockMovement.objects.create(
                stock=destination_stock,
                movement_type='transfer_in',
                quantity=quantity,
                previous_quantity=destination_stock.quantity - quantity,
                new_quantity=destination_stock.quantity,
                user=request.user,
                reason=reason,
                related_movement_type='stock_transfer',
                related_movement_id=source_stock.pk,
            )
            
            messages.success(request, _('Stock transferred successfully.'))
            return redirect('inventory:stock_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = StockTransferForm()
    
    context = {
        'form': form,
        'title': _('Stock Transfer'),
    }
    return render(request, 'inventory/stock_transfer.html', context)


# ==================== STOCK LOCATIONS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def stock_locations(request):
    """List stock locations."""
    locations = StockLocation.objects.filter(is_active=True)
    
    # Search
    query = request.GET.get('q')
    if query:
        locations = locations.filter(
            Q(name__icontains=query) | 
            Q(address__icontains=query) | 
            Q(phone__icontains=query)
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
        'title': _('Stock Locations'),
    }
    return render(request, 'inventory/stock_locations.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_stock_location(request):
    """Create a new stock location."""
    if request.method == 'POST':
        form = WarehouseForm(data=request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.created_by = request.user
            location.save()
            
            messages.success(request, _('Stock location created successfully.'))
            return redirect('inventory:stock_locations')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = WarehouseForm()
    
    context = {
        'form': form,
        'title': _('Create Stock Location'),
    }
    return render(request, 'inventory/create_stock_location.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_stock_location(request, location_id):
    """Edit stock location."""
    location = get_object_or_404(StockLocation, pk=location_id)
    
    if request.method == 'POST':
        form = WarehouseForm(data=request.POST, instance=location)
        if form.is_valid():
            location = form.save()
            messages.success(request, _('Stock location updated.'))
            return redirect('inventory:stock_locations')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = WarehouseForm(instance=location)
    
    context = {
        'location': location,
        'form': form,
        'title': _('Edit Stock Location'),
    }
    return render(request, 'inventory/edit_stock_location.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_stock_location(request, location_id):
    """Delete stock location."""
    location = get_object_or_404(StockLocation, pk=location_id)
    
    # Check if location has stock
    if Stock.objects.filter(location=location).exists():
        messages.error(request, _('Cannot delete location with stock items.'))
        return redirect('inventory:stock_locations')
    
    location.is_active = False
    location.save()
    
    messages.success(request, _('Stock location deleted.'))
    return redirect('inventory:stock_locations')


# ==================== SUPPLIERS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def supplier_list(request):
    """List suppliers."""
    suppliers = Supplier.objects.filter(is_active=True)
    
    # Search
    query = request.GET.get('q')
    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(phone__icontains=query) | 
            Q(address__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(suppliers, 20)
    page = request.GET.get('page')
    
    try:
        suppliers_page = paginator.page(page)
    except PageNotAnInteger:
        suppliers_page = paginator.page(1)
    except EmptyPage:
        suppliers_page = paginator.page(paginator.num_pages)
    
    context = {
        'suppliers': suppliers_page,
        'query': query,
        'title': _('Suppliers'),
    }
    return render(request, 'inventory/supplier_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_supplier(request):
    """Create a new supplier."""
    if request.method == 'POST':
        form = SupplierForm(data=request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()
            
            messages.success(request, _('Supplier created successfully.'))
            return redirect('inventory:supplier_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = SupplierForm()
    
    context = {
        'form': form,
        'title': _('Create Supplier'),
    }
    return render(request, 'inventory/create_supplier.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_supplier(request, supplier_id):
    """Edit supplier."""
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    
    if request.method == 'POST':
        form = SupplierForm(data=request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, _('Supplier updated.'))
            return redirect('inventory:supplier_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = SupplierForm(instance=supplier)
    
    context = {
        'supplier': supplier,
        'form': form,
        'title': _('Edit Supplier'),
    }
    return render(request, 'inventory/edit_supplier.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_supplier(request, supplier_id):
    """Delete supplier."""
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    
    # Check if supplier has purchase orders
    if PurchaseOrder.objects.filter(supplier=supplier).exists():
        messages.error(request, _('Cannot delete supplier with purchase orders.'))
        return redirect('inventory:supplier_list')
    
    supplier.is_active = False
    supplier.save()
    
    messages.success(request, _('Supplier deleted.'))
    return redirect('inventory:supplier_list')


# ==================== PURCHASE ORDERS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def purchase_order_list(request):
    """List purchase orders."""
    orders = PurchaseOrder.objects.filter(
        supplier__is_active=True
    ).select_related('supplier', 'created_by').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter by supplier
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        orders = orders.filter(supplier__id=supplier_id)
    
    # Search
    query = request.GET.get('q')
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) | 
            Q(supplier__name__icontains=query) | 
            Q(notes__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    
    try:
        orders_page = paginator.page(page)
    except PageNotAnInteger:
        orders_page = paginator.page(1)
    except EmptyPage:
        orders_page = paginator.page(paginator.num_pages)
    
    suppliers = Supplier.objects.filter(is_active=True)
    
    context = {
        'orders': orders_page,
        'suppliers': suppliers,
        'current_status': status_filter,
        'current_supplier': supplier_id,
        'query': query,
        'title': _('Purchase Orders'),
    }
    return render(request, 'inventory/purchase_order_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def purchase_order_detail(request, order_id):
    """Purchase order detail."""
    order = get_object_or_404(PurchaseOrder, pk=order_id)
    
    items = PurchaseOrderItem.objects.filter(
        purchase_order=order
    ).select_related('product_variant__product')
    
    context = {
        'order': order,
        'items': items,
        'title': f"{_('Purchase Order')} #{order.order_number}",
    }
    return render(request, 'inventory/purchase_order_detail.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_purchase_order(request):
    """Create a new purchase order."""
    suppliers = Supplier.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = PurchaseOrderForm(data=request.POST)
        if form.is_valid():
            order = PurchaseOrder.objects.create(
                supplier=form.cleaned_data.get('supplier'),
                order_number=f'PO-{timezone.now().strftime("%Y%m%d")}-{PurchaseOrder.objects.count() + 1:04d}',
                expected_delivery_date=form.cleaned_data.get('expected_delivery_date'),
                notes=form.cleaned_data.get('notes'),
                status='draft',
                created_by=request.user,
            )
            
            messages.success(request, _('Purchase order created successfully.'))
            return redirect('inventory:edit_purchase_order', order_id=order.pk)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = PurchaseOrderForm()
    
    context = {
        'form': form,
        'suppliers': suppliers,
        'products': products,
        'title': _('Create Purchase Order'),
    }
    return render(request, 'inventory/create_purchase_order.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_purchase_order(request, order_id):
    """Edit purchase order."""
    order = get_object_or_404(PurchaseOrder, pk=order_id)
    
    if request.method == 'POST':
        form = PurchaseOrderForm(data=request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            messages.success(request, _('Purchase order updated.'))
            return redirect('inventory:purchase_order_detail', order_id=order.pk)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = PurchaseOrderForm(instance=order)
    
    items = PurchaseOrderItem.objects.filter(purchase_order=order)
    
    context = {
        'order': order,
        'form': form,
        'items': items,
        'title': f"{_('Edit Purchase Order')} #{order.order_number}",
    }
    return render(request, 'inventory/edit_purchase_order.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def update_purchase_order_status(request, order_id):
    """Update purchase order status."""
    order = get_object_or_404(PurchaseOrder, pk=order_id)
    new_status = request.POST.get('status')
    
    if new_status not in dict(PurchaseOrder.STATUS_CHOICES):
        messages.error(request, _('Invalid status.'))
        return redirect('inventory:purchase_order_detail', order_id=order.pk)
    
    order.status = new_status
    order.save()
    
    messages.success(request, _('Purchase order status updated.'))
    return redirect('inventory:purchase_order_detail', order_id=order.pk)


# ==================== LOW STOCK ALERTS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def low_stock_alerts(request):
    """List low stock alerts."""
    alerts = LowStockAlert.objects.filter(
        is_resolved=False
    ).select_related('stock__product_variant__product', 'stock__location').order_by('-created_at')
    
    # Filter by product
    product_id = request.GET.get('product')
    if product_id:
        alerts = alerts.filter(stock__product_variant__product__id=product_id)
    
    # Filter by location
    location_id = request.GET.get('location')
    if location_id:
        alerts = alerts.filter(stock__location__id=location_id)
    
    # Filter by resolved
    resolved = request.GET.get('resolved')
    if resolved:
        alerts = alerts.filter(is_resolved=True)
    
    # Pagination
    paginator = Paginator(alerts, 20)
    page = request.GET.get('page')
    
    try:
        alerts_page = paginator.page(page)
    except PageNotAnInteger:
        alerts_page = paginator.page(1)
    except EmptyPage:
        alerts_page = paginator.page(paginator.num_pages)
    
    products = Product.objects.filter(is_active=True)[:100]
    locations = StockLocation.objects.filter(is_active=True)
    
    context = {
        'alerts': alerts_page,
        'products': products,
        'locations': locations,
        'current_product': product_id,
        'current_location': location_id,
        'title': _('Low Stock Alerts'),
    }
    return render(request, 'inventory/low_stock_alerts.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def resolve_low_stock_alert(request, alert_id):
    """Resolve a low stock alert."""
    alert = get_object_or_404(LowStockAlert, pk=alert_id)
    
    alert.is_resolved = True
    alert.resolved_by = request.user
    alert.resolved_at = timezone.now()
    alert.save()
    
    messages.success(request, _('Low stock alert resolved.'))
    return redirect('inventory:low_stock_alerts')


# ==================== INVENTORY REPORTS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def inventory_reports(request):
    """List inventory reports."""
    reports = InventoryReport.objects.filter(
        generated_by=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reports, 20)
    page = request.GET.get('page')
    
    try:
        reports_page = paginator.page(page)
    except PageNotAnInteger:
        reports_page = paginator.page(1)
    except EmptyPage:
        reports_page = paginator.page(paginator.num_pages)
    
    context = {
        'reports': reports_page,
        'title': _('Inventory Reports'),
    }
    return render(request, 'inventory/inventory_reports.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def generate_inventory_report(request):
    """Generate inventory report."""
    report_type = request.POST.get('report_type', 'stock_levels')
    
    # Generate report based on type
    if report_type == 'stock_levels':
        report = generate_stock_levels_report(request.user)
    elif report_type == 'low_stock':
        report = generate_low_stock_report(request.user)
    elif report_type == 'movements':
        report = generate_stock_movements_report(request.user)
    else:
        messages.error(request, _('Invalid report type.'))
        return redirect('inventory:inventory_reports')
    
    messages.success(request, _('Inventory report generated successfully.'))
    return redirect('inventory:inventory_reports')


def generate_stock_levels_report(user):
    """Generate stock levels report."""
    report = InventoryReport.objects.create(
        report_type='stock_levels',
        title='Stock Levels Report',
        data={},
        generated_by=user,
    )
    
    # Get all stocks
    stocks = Stock.objects.all().select_related('product_variant__product', 'location')
    
    report_data = {
        'total_items': stocks.count(),
        'total_quantity': sum(s.quantity for s in stocks),
        'total_value': sum(
            s.quantity * s.product_variant.get_price()
            for s in stocks
        ),
        'by_location': {},
        'by_product': {},
    }
    
    for stock in stocks:
        # By location
        location_name = stock.location.name
        if location_name not in report_data['by_location']:
            report_data['by_location'][location_name] = {
                'quantity': 0,
                'value': 0,
                'items': 0,
            }
        report_data['by_location'][location_name]['quantity'] += stock.quantity
        report_data['by_location'][location_name]['value'] += stock.quantity * stock.product_variant.get_price()
        report_data['by_location'][location_name]['items'] += 1
        
        # By product
        product_name = stock.product_variant.product.name
        if product_name not in report_data['by_product']:
            report_data['by_product'][product_name] = {
                'quantity': 0,
                'value': 0,
                'variants': {},
            }
        report_data['by_product'][product_name]['quantity'] += stock.quantity
        report_data['by_product'][product_name]['value'] += stock.quantity * stock.product_variant.get_price()
        
        variant_name = stock.product_variant.name or stock.product_variant.product.name
        if variant_name not in report_data['by_product'][product_name]['variants']:
            report_data['by_product'][product_name]['variants'][variant_name] = {
                'quantity': 0,
                'value': 0,
            }
        report_data['by_product'][product_name]['variants'][variant_name]['quantity'] += stock.quantity
        report_data['by_product'][product_name]['variants'][variant_name]['value'] += stock.quantity * stock.product_variant.get_price()
    
    report.data = report_data
    report.save()
    
    return report


def generate_low_stock_report(user):
    """Generate low stock report."""
    report = InventoryReport.objects.create(
        report_type='low_stock',
        title='Low Stock Report',
        data={},
        generated_by=user,
    )
    
    # Get low stock items
    low_stock_items = Stock.objects.filter(
        quantity__lte=F('product_variant__low_stock_threshold')
    ).select_related('product_variant__product', 'location')
    
    report_data = {
        'total_low_stock_items': low_stock_items.count(),
        'items': [],
        'by_location': {},
    }
    
    for stock in low_stock_items:
        report_data['items'].append({
            'product': stock.product_variant.product.name,
            'variant': stock.product_variant.name or '',
            'sku': stock.product_variant.sku,
            'location': stock.location.name,
            'quantity': stock.quantity,
            'threshold': stock.product_variant.low_stock_threshold,
        })
        
        location_name = stock.location.name
        if location_name not in report_data['by_location']:
            report_data['by_location'][location_name] = 0
        report_data['by_location'][location_name] += 1
    
    report.data = report_data
    report.save()
    
    return report


def generate_stock_movements_report(user):
    """Generate stock movements report."""
    report = InventoryReport.objects.create(
        report_type='movements',
        title='Stock Movements Report',
        data={},
        generated_by=user,
    )
    
    # Get recent movements
    movements = StockMovement.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).select_related('stock__product_variant__product', 'stock__location', 'user')
    
    report_data = {
        'period': {
            'start': (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d'),
            'end': timezone.now().strftime('%Y-%m-%d'),
        },
        'total_movements': movements.count(),
        'by_type': {},
        'by_user': {},
        'by_product': {},
    }
    
    for movement in movements:
        # By type
        movement_type = movement.movement_type
        if movement_type not in report_data['by_type']:
            report_data['by_type'][movement_type] = {
                'count': 0,
                'total_quantity': 0,
            }
        report_data['by_type'][movement_type]['count'] += 1
        report_data['by_type'][movement_type]['total_quantity'] += movement.quantity
        
        # By user
        user_name = movement.user.get_full_name() or movement.user.username
        if user_name not in report_data['by_user']:
            report_data['by_user'][user_name] = {
                'count': 0,
                'total_quantity': 0,
            }
        report_data['by_user'][user_name]['count'] += 1
        report_data['by_user'][user_name]['total_quantity'] += movement.quantity
        
        # By product
        product_name = movement.stock.product_variant.product.name
        if product_name not in report_data['by_product']:
            report_data['by_product'][product_name] = {
                'count': 0,
                'total_quantity': 0,
            }
        report_data['by_product'][product_name]['count'] += 1
        report_data['by_product'][product_name]['total_quantity'] += movement.quantity
    
    report.data = report_data
    report.save()
    
    return report


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def inventory_report_detail(request, report_id):
    """Inventory report detail."""
    report = get_object_or_404(InventoryReport, pk=report_id)
    
    context = {
        'report': report,
        'title': report.title,
    }
    return render(request, 'inventory/inventory_report_detail.html', context)


# ==================== DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def inventory_dashboard(request):
    """Inventory dashboard."""
    # Get counts
    total_products = Product.objects.filter(is_active=True).count()
    total_variants = ProductVariant.objects.filter(is_active=True).count()
    total_stock = Stock.objects.aggregate(total=Sum('quantity'))['total'] or 0
    low_stock_count = Stock.objects.filter(
        quantity__lte=F('product_variant__low_stock_threshold')
    ).count()
    
    # Get recent movements
    recent_movements = StockMovement.objects.select_related(
        'stock__product_variant__product',
        'user'
    ).order_by('-created_at')[:10]
    
    # Get low stock items
    low_stock_items = Stock.objects.filter(
        quantity__lte=F('product_variant__low_stock_threshold')
    ).select_related('product_variant__product', 'location')[:10]
    
    # Get stock by location
    stock_by_location = Stock.objects.values('location__name').annotate(
        total=Sum('quantity')
    ).order_by('-total')
    
    # Get stock value by product
    stock_value_by_product = Stock.objects.values('product_variant__product__name').annotate(
        total_value=Sum('quantity') * F('product_variant__price')
    ).order_by('-total_value')[:10]
    
    context = {
        'total_products': total_products,
        'total_variants': total_variants,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'recent_movements': recent_movements,
        'low_stock_items': low_stock_items,
        'stock_by_location': stock_by_location,
        'stock_value_by_product': stock_value_by_product,
        'title': _('Inventory Dashboard'),
    }
    return render(request, 'inventory/inventory_dashboard.html', context)


# ==================== AJAX VIEWS ====================

@login_required
@require_http_methods(["GET"])
def get_stock_level_ajax(request, variant_id, location_id=None):
    """Get stock level via AJAX."""
    if location_id:
        stock = get_object_or_404(Stock, product_variant__id=variant_id, location__id=location_id)
    else:
        stock = Stock.objects.filter(
            product_variant__id=variant_id
        ).order_by('-quantity').first()
    
    if not stock:
        return JsonResponse({'error': 'Stock not found'}, status=404)
    
    return JsonResponse({
        'quantity': stock.quantity,
        'location': stock.location.name if stock.location else None,
        'status': stock.status,
        'low_stock_threshold': stock.product_variant.low_stock_threshold,
        'is_low_stock': stock.quantity <= stock.product_variant.low_stock_threshold,
    })


@login_required
@require_http_methods(["GET"])
def get_stock_by_location_ajax(request, location_id):
    """Get stock by location via AJAX."""
    location = get_object_or_404(StockLocation, pk=location_id)
    
    stocks = Stock.objects.filter(
        location=location
    ).select_related('product_variant__product')
    
    stocks_data = []
    for stock in stocks:
        stocks_data.append({
            'id': str(stock.id),
            'product': stock.product_variant.product.name,
            'variant': stock.product_variant.name or '',
            'sku': stock.product_variant.sku,
            'quantity': stock.quantity,
            'status': stock.status,
        })
    
    return JsonResponse({
        'location': location.name,
        'stocks': stocks_data,
        'total': len(stocks_data),
        'total_quantity': sum(s.quantity for s in stocks),
    })


@login_required
@require_http_methods(["POST"])
def update_stock_status_ajax(request):
    """Update stock status via AJAX."""
    stock_id = request.POST.get('stock_id')
    new_status = request.POST.get('status')
    
    stock = get_object_or_404(Stock, pk=stock_id)
    
    if new_status not in dict(StockStatus.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    old_status = stock.status
    stock.status = new_status
    stock.save()
    
    # Create movement record
    StockMovement.objects.create(
        stock=stock,
        movement_type='status_change',
        quantity=0,
        previous_quantity=stock.quantity,
        new_quantity=stock.quantity,
        user=request.user,
        reason=f'Status changed from {old_status} to {new_status}',
    )
    
    return JsonResponse({
        'success': True,
        'new_status': new_status,
    })


@login_required
@require_http_methods(["GET"])
def get_low_stock_alerts_ajax(request):
    """Get low stock alerts via AJAX."""
    unresolved_only = request.GET.get('unresolved_only', 'true') == 'true'
    
    alerts = LowStockAlert.objects.filter(
        is_resolved=False
    ).select_related('stock__product_variant__product', 'stock__location')
    
    if unresolved_only:
        alerts = alerts.filter(is_resolved=False)
    
    alerts_data = []
    for alert in alerts:
        alerts_data.append({
            'id': str(alert.id),
            'product': alert.stock.product_variant.product.name,
            'variant': alert.stock.product_variant.name or '',
            'sku': alert.stock.product_variant.sku,
            'location': alert.stock.location.name,
            'current_quantity': alert.current_quantity,
            'threshold': alert.threshold,
            'created_at': alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({
        'alerts': alerts_data,
        'total': len(alerts_data),
    })


@login_required
@require_http_methods(["GET"])
def get_inventory_summary_ajax(request):
    """Get inventory summary via AJAX."""
    total_stock = Stock.objects.aggregate(total=Sum('quantity'))['total'] or 0
    low_stock_count = Stock.objects.filter(
        quantity__lte=F('product_variant__low_stock_threshold')
    ).count()
    
    total_products = Product.objects.filter(is_active=True).count()
    total_variants = ProductVariant.objects.filter(is_active=True).count()
    
    return JsonResponse({
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'total_products': total_products,
        'total_variants': total_variants,
    })
