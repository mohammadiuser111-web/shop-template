"""
Views for dashboard app (admin panel).
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
from django.db.models import Q, Sum, Count, F, DecimalField
from django.db.models.functions import Coalesce, ExtractDay, ExtractMonth, ExtractYear
from django.utils import timezone
from django.conf import settings

from .models import (
    DashboardWidget, DashboardLayout, DashboardStatistic,
    QuickAction, AdminNote, SystemLog
)
from .forms import (
    DashboardWidgetForm, DashboardLayoutForm, QuickActionForm,
    AdminNoteForm, SystemLogSearchForm
)
from apps.orders.models import Order, OrderItem
from apps.products.models import Product, Category, Brand, ProductVariant
from apps.accounts.models import User, UserAddress
from apps.reviews.models import Review
from apps.support.models import Ticket
from apps.payments.models import Payment
from apps.inventory.models import Stock, StockMovement
from apps.discounts.models import Coupon, DiscountUsage
from apps.ads.models import Ad, AdCampaign, AdClick, AdConversion
from apps.blog.models import Article


def is_staff(user):
    """Check if user is staff."""
    return user.is_staff


def is_superuser(user):
    """Check if user is superuser."""
    return user.is_superuser


# ==================== MAIN DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def dashboard(request):
    """Main admin dashboard."""
    # Get user's dashboard layout
    layout = DashboardLayout.objects.filter(user=request.user).first()
    
    # Get statistics
    stats = get_dashboard_statistics(request.user)
    
    # Get recent activity
    recent_activity = get_recent_activity(request.user)
    
    # Get quick actions
    quick_actions = QuickAction.objects.filter(is_active=True)[:10]
    
    # Get widgets
    widgets = DashboardWidget.objects.filter(
        is_active=True
    ).order_by('position')
    
    context = {
        'layout': layout,
        'stats': stats,
        'recent_activity': recent_activity,
        'quick_actions': quick_actions,
        'widgets': widgets,
        'title': _('Dashboard'),
    }
    return render(request, 'dashboard/dashboard.html', context)


def get_dashboard_statistics(user):
    """Get dashboard statistics."""
    # Time period
    today = timezone.now().date()
    this_week_start = today - timezone.timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timezone.timedelta(days=1)).replace(day=1)
    
    # Sales statistics
    total_sales = Order.objects.filter(
        status__in=['completed', 'delivered', 'paid']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    today_sales = Order.objects.filter(
        status__in=['completed', 'delivered', 'paid'],
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    this_week_sales = Order.objects.filter(
        status__in=['completed', 'delivered', 'paid'],
        created_at__date__gte=this_week_start
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    this_month_sales = Order.objects.filter(
        status__in=['completed', 'delivered', 'paid'],
        created_at__date__gte=this_month_start
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status__in=['completed', 'delivered']).count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Product statistics
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_products = ProductVariant.objects.filter(
        is_active=True,
        stock__quantity__lte=F('low_stock_threshold')
    ).distinct().count()
    
    # Customer statistics
    total_customers = User.objects.filter(is_active=True).count()
    new_customers_today = User.objects.filter(
        is_active=True,
        date_joined__date=today
    ).count()
    active_customers = User.objects.filter(
        is_active=True,
        last_login__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    
    # Review statistics
    total_reviews = Review.objects.filter(is_approved=True).count()
    avg_rating = Review.objects.filter(is_approved=True).aggregate(
        avg=Coalesce(Sum('overall_rating') / Count('id'), 0)
    )['avg'] or 0
    
    # Support statistics
    open_tickets = Ticket.objects.filter(status='open').count()
    pending_tickets = Ticket.objects.filter(status='pending').count()
    
    # Payment statistics
    total_payments = Payment.objects.filter(status='completed').count()
    total_refunds = Payment.objects.filter(status='refunded').count()
    
    # Ad statistics
    total_ads = Ad.objects.count()
    active_campaigns = AdCampaign.objects.filter(status='active').count()
    
    return {
        'sales': {
            'total': total_sales,
            'today': today_sales,
            'this_week': this_week_sales,
            'this_month': this_month_sales,
        },
        'orders': {
            'total': total_orders,
            'pending': pending_orders,
            'completed': completed_orders,
            'cancelled': cancelled_orders,
        },
        'products': {
            'total': total_products,
            'low_stock': low_stock_products,
        },
        'customers': {
            'total': total_customers,
            'new_today': new_customers_today,
            'active': active_customers,
        },
        'reviews': {
            'total': total_reviews,
            'avg_rating': round(avg_rating, 1),
        },
        'support': {
            'open_tickets': open_tickets,
            'pending_tickets': pending_tickets,
        },
        'payments': {
            'total': total_payments,
            'refunds': total_refunds,
        },
        'ads': {
            'total_ads': total_ads,
            'active_campaigns': active_campaigns,
        },
    }


def get_recent_activity(user):
    """Get recent activity for dashboard."""
    # Get recent orders
    recent_orders = Order.objects.filter(
        status__in=['pending', 'processing', 'shipped', 'delivered', 'completed']
    ).select_related('user').order_by('-created_at')[:5]
    
    # Get recent products
    recent_products = Product.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    # Get recent customers
    recent_customers = User.objects.filter(is_active=True).order_by('-date_joined')[:5]
    
    # Get recent reviews
    recent_reviews = Review.objects.filter(is_approved=True).select_related(
        'user', 'product'
    ).order_by('-created_at')[:5]
    
    # Get recent tickets
    recent_tickets = Ticket.objects.order_by('-created_at')[:5]
    
    # Get system logs
    system_logs = SystemLog.objects.order_by('-created_at')[:5]
    
    return {
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'recent_customers': recent_customers,
        'recent_reviews': recent_reviews,
        'recent_tickets': recent_tickets,
        'system_logs': system_logs,
    }


# ==================== SALES DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def sales_dashboard(request):
    """Sales dashboard."""
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = timezone.now().strftime('%Y-%m-%d')
    
    # Get sales data
    sales_data = get_sales_data(start_date, end_date)
    
    # Get top selling products
    top_products = get_top_selling_products(start_date, end_date, limit=10)
    
    # Get sales by category
    sales_by_category = get_sales_by_category(start_date, end_date)
    
    # Get sales by day
    sales_by_day = get_sales_by_day(start_date, end_date)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'sales_data': sales_data,
        'top_products': top_products,
        'sales_by_category': sales_by_category,
        'sales_by_day': sales_by_day,
        'title': _('Sales Dashboard'),
    }
    return render(request, 'dashboard/sales_dashboard.html', context)


def get_sales_data(start_date, end_date):
    """Get sales data for a date range."""
    orders = Order.objects.filter(
        status__in=['completed', 'delivered', 'paid'],
        created_at__date__range=[start_date, end_date]
    )
    
    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = orders.count()
    avg_order_value = orders.aggregate(avg=Coalesce(Sum('total_amount') / Count('id'), 0))['avg'] or 0
    
    return {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': round(avg_order_value, 2),
    }


def get_top_selling_products(start_date, end_date, limit=10):
    """Get top selling products."""
    top_products = OrderItem.objects.filter(
        order__status__in=['completed', 'delivered', 'paid'],
        order__created_at__date__range=[start_date, end_date]
    ).values('product__name', 'product__slug').annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum('price') * Sum('quantity')
    ).order_by('-total_sales')[:limit]
    
    return list(top_products)


def get_sales_by_category(start_date, end_date):
    """Get sales by category."""
    sales_by_category = OrderItem.objects.filter(
        order__status__in=['completed', 'delivered', 'paid'],
        order__created_at__date__range=[start_date, end_date]
    ).values('product__categories__name').annotate(
        total_sales=Sum('price') * Sum('quantity')
    ).order_by('-total_sales')
    
    return list(sales_by_category)


def get_sales_by_day(start_date, end_date):
    """Get sales by day."""
    sales_by_day = Order.objects.filter(
        status__in=['completed', 'delivered', 'paid'],
        created_at__date__range=[start_date, end_date]
    ).annotate(
        day=ExtractDay('created_at')
    ).values('day').annotate(
        total_sales=Sum('total_amount')
    ).order_by('day')
    
    return list(sales_by_day)


# ==================== PRODUCTS DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def products_dashboard(request):
    """Products dashboard."""
    # Get statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_variants = ProductVariant.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_brands = Brand.objects.filter(is_active=True).count()
    
    # Get product status
    in_stock = ProductVariant.objects.filter(
        is_active=True,
        stock__quantity__gt=0
    ).distinct().count()
    
    out_of_stock = ProductVariant.objects.filter(
        is_active=True,
        stock__quantity=0
    ).distinct().count()
    
    low_stock = ProductVariant.objects.filter(
        is_active=True,
        stock__quantity__lte=F('low_stock_threshold')
    ).distinct().count()
    
    # Get top rated products
    top_rated = Product.objects.filter(is_active=True).annotate(
        avg_rating=Coalesce(Sum('reviews__overall_rating') / Count('reviews'), 0),
        review_count=Count('reviews')
    ).filter(review_count__gt=0).order_by('-avg_rating')[:10]
    
    # Get most viewed products
    most_viewed = Product.objects.filter(is_active=True).order_by('-view_count')[:10]
    
    # Get best selling products
    best_selling = Product.objects.filter(is_active=True).annotate(
        total_sold=Sum('order_items__quantity')
    ).order_by('-total_sold')[:10]
    
    # Get products by category
    products_by_category = Product.objects.filter(is_active=True).values('categories__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_products': total_products,
        'total_variants': total_variants,
        'total_categories': total_categories,
        'total_brands': total_brands,
        'in_stock': in_stock,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'top_rated': top_rated,
        'most_viewed': most_viewed,
        'best_selling': best_selling,
        'products_by_category': products_by_category,
        'title': _('Products Dashboard'),
    }
    return render(request, 'dashboard/products_dashboard.html', context)


# ==================== CUSTOMERS DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def customers_dashboard(request):
    """Customers dashboard."""
    # Get statistics
    total_customers = User.objects.filter(is_active=True).count()
    new_customers = User.objects.filter(
        is_active=True,
        date_joined__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    active_customers = User.objects.filter(
        is_active=True,
        last_login__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    inactive_customers = User.objects.filter(
        is_active=True,
        last_login__lt=timezone.now() - timezone.timedelta(days=30)
    ).count()
    
    # Get customers by registration date
    customers_by_date = User.objects.filter(is_active=True).annotate(
        date=ExtractDay('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Get top customers by orders
    top_customers = User.objects.filter(is_active=True).annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).order_by('-total_spent')[:10]
    
    # Get customers by location
    customers_by_location = UserAddress.objects.values('country').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Get customer loyalty
    loyal_customers = User.objects.filter(
        is_active=True,
        orders__created_at__gte=timezone.now() - timezone.timedelta(days=90)
    ).annotate(
        order_count=Count('orders')
    ).filter(order_count__gte=3).count()
    
    context = {
        'total_customers': total_customers,
        'new_customers': new_customers,
        'active_customers': active_customers,
        'inactive_customers': inactive_customers,
        'customers_by_date': customers_by_date,
        'top_customers': top_customers,
        'customers_by_location': customers_by_location,
        'loyal_customers': loyal_customers,
        'title': _('Customers Dashboard'),
    }
    return render(request, 'dashboard/customers_dashboard.html', context)


# ==================== ORDERS DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def orders_dashboard(request):
    """Orders dashboard."""
    # Get statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Get orders by status
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get orders by day
    orders_by_day = Order.objects.annotate(
        day=ExtractDay('created_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Get average order value
    avg_order_value = Order.objects.filter(
        status__in=['completed', 'delivered', 'paid']
    ).aggregate(avg=Coalesce(Sum('total_amount') / Count('id'), 0))['avg'] or 0
    
    # Get orders by payment method
    orders_by_payment = Order.objects.values('payment_method').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get orders by shipping method
    orders_by_shipping = Order.objects.values('shipping_method').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'orders_by_status': orders_by_status,
        'orders_by_day': orders_by_day,
        'avg_order_value': round(avg_order_value, 2),
        'orders_by_payment': orders_by_payment,
        'orders_by_shipping': orders_by_shipping,
        'recent_orders': recent_orders,
        'title': _('Orders Dashboard'),
    }
    return render(request, 'dashboard/orders_dashboard.html', context)


# ==================== MARKETING DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def marketing_dashboard(request):
    """Marketing dashboard."""
    # Get ad statistics
    total_ads = Ad.objects.count()
    active_ads = Ad.objects.filter(status='active').count()
    total_campaigns = AdCampaign.objects.count()
    active_campaigns = AdCampaign.objects.filter(status='active').count()
    
    # Get ad performance
    total_clicks = AdClick.objects.count()
    total_impressions = AdImpression.objects.count()
    total_conversions = AdConversion.objects.count()
    total_spent = Ad.objects.aggregate(total=Sum('cost_per_click'))['total'] or 0
    
    # Get top performing ads
    top_ads = Ad.objects.annotate(
        total_clicks=Count('adclick'),
        total_conversions=Count('adconversion')
    ).order_by('-total_clicks')[:10]
    
    # Get top performing campaigns
    top_campaigns = AdCampaign.objects.annotate(
        total_clicks=Count('ad__adclick'),
        total_conversions=Count('ad__adconversion')
    ).order_by('-total_clicks')[:10]
    
    # Get conversion rate
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    
    # Get CTR
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    # Get ROI
    total_revenue = AdConversion.objects.aggregate(total=Sum('conversion_value'))['total'] or 0
    roi = (total_revenue / total_spent * 100) if total_spent > 0 else 0
    
    # Get coupon statistics
    total_coupons = Coupon.objects.count()
    active_coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    ).count()
    total_discounts = DiscountUsage.objects.count()
    total_discount_value = DiscountUsage.objects.aggregate(total=Sum('discount_amount'))['total'] or 0
    
    # Get most used coupons
    most_used_coupons = DiscountUsage.objects.values('coupon__code', 'coupon__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'total_ads': total_ads,
        'active_ads': active_ads,
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'total_clicks': total_clicks,
        'total_impressions': total_impressions,
        'total_conversions': total_conversions,
        'total_spent': total_spent,
        'top_ads': top_ads,
        'top_campaigns': top_campaigns,
        'conversion_rate': round(conversion_rate, 2),
        'ctr': round(ctr, 2),
        'roi': round(roi, 2),
        'total_coupons': total_coupons,
        'active_coupons': active_coupons,
        'total_discounts': total_discounts,
        'total_discount_value': total_discount_value,
        'most_used_coupons': most_used_coupons,
        'title': _('Marketing Dashboard'),
    }
    return render(request, 'dashboard/marketing_dashboard.html', context)


# ==================== SUPPORT DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def support_dashboard(request):
    """Support dashboard."""
    # Get ticket statistics
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='open').count()
    pending_tickets = Ticket.objects.filter(status='pending').count()
    in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    closed_tickets = Ticket.objects.filter(status='closed').count()
    
    # Get tickets by status
    tickets_by_status = Ticket.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get tickets by category
    tickets_by_category = Ticket.objects.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get tickets by priority
    tickets_by_priority = Ticket.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get average response time
    avg_response_time = Ticket.objects.filter(
        status__in=['resolved', 'closed'],
        first_response_at__isnull=False
    ).aggregate(avg=Coalesce(Sum('first_response_at') / Count('id'), 0))['avg'] or 0
    
    # Get average resolution time
    avg_resolution_time = Ticket.objects.filter(
        status__in=['resolved', 'closed'],
        resolved_at__isnull=False
    ).aggregate(avg=Coalesce(Sum('resolved_at') / Count('id'), 0))['avg'] or 0
    
    # Get recent tickets
    recent_tickets = Ticket.objects.order_by('-created_at')[:10]
    
    # Get unresolved tickets
    unresolved_tickets = Ticket.objects.filter(
        status__in=['open', 'pending', 'in_progress']
    ).order_by('-created_at')[:10]
    
    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'pending_tickets': pending_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'tickets_by_status': tickets_by_status,
        'tickets_by_category': tickets_by_category,
        'tickets_by_priority': tickets_by_priority,
        'avg_response_time': avg_response_time,
        'avg_resolution_time': avg_resolution_time,
        'recent_tickets': recent_tickets,
        'unresolved_tickets': unresolved_tickets,
        'title': _('Support Dashboard'),
    }
    return render(request, 'dashboard/support_dashboard.html', context)


# ==================== INVENTORY DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def inventory_dashboard(request):
    """Inventory dashboard."""
    # Get statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_variants = ProductVariant.objects.filter(is_active=True).count()
    total_stock = Stock.objects.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Get stock status
    in_stock = ProductVariant.objects.filter(
        is_active=True,
        stock__quantity__gt=0
    ).distinct().count()
    
    out_of_stock = ProductVariant.objects.filter(
        is_active=True,
        stock__quantity=0
    ).distinct().count()
    
    low_stock = ProductVariant.objects.filter(
        is_active=True,
        stock__quantity__lte=F('low_stock_threshold')
    ).distinct().count()
    
    # Get stock by location
    stock_by_location = Stock.objects.values('location__name').annotate(
        total=Sum('quantity')
    ).order_by('-total')
    
    # Get stock movements
    recent_movements = StockMovement.objects.select_related(
        'stock__product_variant__product',
        'user'
    ).order_by('-created_at')[:10]
    
    # Get low stock items
    low_stock_items = Stock.objects.filter(
        quantity__lte=F('product_variant__low_stock_threshold')
    ).select_related('product_variant__product', 'location')[:10]
    
    # Get stock value
    stock_value = Stock.objects.aggregate(
        total=Sum('quantity') * F('product_variant__price')
    )['total'] or 0
    
    context = {
        'total_products': total_products,
        'total_variants': total_variants,
        'total_stock': total_stock,
        'in_stock': in_stock,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'stock_by_location': stock_by_location,
        'recent_movements': recent_movements,
        'low_stock_items': low_stock_items,
        'stock_value': stock_value,
        'title': _('Inventory Dashboard'),
    }
    return render(request, 'dashboard/inventory_dashboard.html', context)


# ==================== REPORTS DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def reports_dashboard(request):
    """Reports dashboard."""
    # Get report types
    report_types = [
        {'id': 'sales', 'name': _('Sales Report')},
        {'id': 'orders', 'name': _('Orders Report')},
        {'id': 'customers', 'name': _('Customers Report')},
        {'id': 'products', 'name': _('Products Report')},
        {'id': 'inventory', 'name': _('Inventory Report')},
        {'id': 'marketing', 'name': _('Marketing Report')},
        {'id': 'support', 'name': _('Support Report')},
    ]
    
    context = {
        'report_types': report_types,
        'title': _('Reports Dashboard'),
    }
    return render(request, 'dashboard/reports_dashboard.html', context)


# ==================== WIDGETS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def widget_list(request):
    """List dashboard widgets."""
    widgets = DashboardWidget.objects.filter(is_active=True)
    
    context = {
        'widgets': widgets,
        'title': _('Dashboard Widgets'),
    }
    return render(request, 'dashboard/widget_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_widget(request):
    """Create a new dashboard widget."""
    if request.method == 'POST':
        form = DashboardWidgetForm(data=request.POST)
        if form.is_valid():
            widget = form.save(commit=False)
            widget.created_by = request.user
            widget.save()
            
            messages.success(request, _('Dashboard widget created successfully.'))
            return redirect('dashboard:widget_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = DashboardWidgetForm()
    
    context = {
        'form': form,
        'title': _('Create Dashboard Widget'),
    }
    return render(request, 'dashboard/create_widget.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_widget(request, widget_id):
    """Edit a dashboard widget."""
    widget = get_object_or_404(DashboardWidget, pk=widget_id)
    
    if request.method == 'POST':
        form = DashboardWidgetForm(data=request.POST, instance=widget)
        if form.is_valid():
            widget = form.save()
            messages.success(request, _('Dashboard widget updated.'))
            return redirect('dashboard:widget_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = DashboardWidgetForm(instance=widget)
    
    context = {
        'widget': widget,
        'form': form,
        'title': _('Edit Dashboard Widget'),
    }
    return render(request, 'dashboard/edit_widget.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_widget(request, widget_id):
    """Delete a dashboard widget."""
    widget = get_object_or_404(DashboardWidget, pk=widget_id)
    widget.delete()
    messages.success(request, _('Dashboard widget deleted.'))
    return redirect('dashboard:widget_list')


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def update_widget_position(request):
    """Update widget positions via AJAX."""
    widget_ids = request.POST.getlist('widget_ids[]')
    
    for index, widget_id in enumerate(widget_ids):
        widget = get_object_or_404(DashboardWidget, pk=widget_id)
        widget.position = index
        widget.save()
    
    return JsonResponse({'success': True})


# ==================== LAYOUTS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def dashboard_layout(request):
    """Manage dashboard layout."""
    layout, created = DashboardLayout.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = DashboardLayoutForm(data=request.POST, instance=layout)
        if form.is_valid():
            layout = form.save()
            messages.success(request, _('Dashboard layout updated.'))
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = DashboardLayoutForm(instance=layout)
    
    context = {
        'layout': layout,
        'form': form,
        'title': _('Dashboard Layout'),
    }
    return render(request, 'dashboard/dashboard_layout.html', context)


# ==================== QUICK ACTIONS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def quick_action_list(request):
    """List quick actions."""
    actions = QuickAction.objects.filter(is_active=True)
    
    context = {
        'actions': actions,
        'title': _('Quick Actions'),
    }
    return render(request, 'dashboard/quick_action_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_quick_action(request):
    """Create a new quick action."""
    if request.method == 'POST':
        form = QuickActionForm(data=request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.created_by = request.user
            action.save()
            
            messages.success(request, _('Quick action created successfully.'))
            return redirect('dashboard:quick_action_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = QuickActionForm()
    
    context = {
        'form': form,
        'title': _('Create Quick Action'),
    }
    return render(request, 'dashboard/create_quick_action.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_quick_action(request, action_id):
    """Edit a quick action."""
    action = get_object_or_404(QuickAction, pk=action_id)
    
    if request.method == 'POST':
        form = QuickActionForm(data=request.POST, instance=action)
        if form.is_valid():
            action = form.save()
            messages.success(request, _('Quick action updated.'))
            return redirect('dashboard:quick_action_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = QuickActionForm(instance=action)
    
    context = {
        'action': action,
        'form': form,
        'title': _('Edit Quick Action'),
    }
    return render(request, 'dashboard/edit_quick_action.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_quick_action(request, action_id):
    """Delete a quick action."""
    action = get_object_or_404(QuickAction, pk=action_id)
    action.delete()
    messages.success(request, _('Quick action deleted.'))
    return redirect('dashboard:quick_action_list')


# ==================== ADMIN NOTES ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def admin_note_list(request):
    """List admin notes."""
    notes = AdminNote.objects.filter(
        created_by=request.user
    ).order_by('-created_at')
    
    # Search
    query = request.GET.get('q')
    if query:
        notes = notes.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(notes, 20)
    page = request.GET.get('page')
    
    try:
        notes_page = paginator.page(page)
    except PageNotAnInteger:
        notes_page = paginator.page(1)
    except EmptyPage:
        notes_page = paginator.page(paginator.num_pages)
    
    context = {
        'notes': notes_page,
        'query': query,
        'title': _('Admin Notes'),
    }
    return render(request, 'dashboard/admin_note_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_admin_note(request):
    """Create a new admin note."""
    if request.method == 'POST':
        form = AdminNoteForm(data=request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.created_by = request.user
            note.save()
            
            messages.success(request, _('Admin note created successfully.'))
            return redirect('dashboard:admin_note_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdminNoteForm()
    
    context = {
        'form': form,
        'title': _('Create Admin Note'),
    }
    return render(request, 'dashboard/create_admin_note.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_admin_note(request, note_id):
    """Edit an admin note."""
    note = get_object_or_404(AdminNote, pk=note_id, created_by=request.user)
    
    if request.method == 'POST':
        form = AdminNoteForm(data=request.POST, instance=note)
        if form.is_valid():
            note = form.save()
            messages.success(request, _('Admin note updated.'))
            return redirect('dashboard:admin_note_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdminNoteForm(instance=note)
    
    context = {
        'note': note,
        'form': form,
        'title': _('Edit Admin Note'),
    }
    return render(request, 'dashboard/edit_admin_note.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_admin_note(request, note_id):
    """Delete an admin note."""
    note = get_object_or_404(AdminNote, pk=note_id, created_by=request.user)
    note.delete()
    messages.success(request, _('Admin note deleted.'))
    return redirect('dashboard:admin_note_list')


# ==================== SYSTEM LOGS ====================

@login_required
@user_passes_test(is_superuser)
@require_http_methods(["GET"])
def system_log_list(request):
    """List system logs."""
    logs = SystemLog.objects.all()
    
    # Filter by level
    level_filter = request.GET.get('level')
    if level_filter:
        logs = logs.filter(level=level_filter)
    
    # Filter by user
    user_filter = request.GET.get('user')
    if user_filter:
        logs = logs.filter(user__id=user_filter)
    
    # Search
    query = request.GET.get('q')
    if query:
        logs = logs.filter(
            Q(message__icontains=query) | 
            Q(action__icontains=query) | 
            Q(ip_address__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    
    try:
        logs_page = paginator.page(page)
    except PageNotAnInteger:
        logs_page = paginator.page(1)
    except EmptyPage:
        logs_page = paginator.page(paginator.num_pages)
    
    users = User.objects.filter(is_staff=True)
    
    context = {
        'logs': logs_page,
        'users': users,
        'current_level': level_filter,
        'current_user': user_filter,
        'query': query,
        'title': _('System Logs'),
    }
    return render(request, 'dashboard/system_log_list.html', context)


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["GET"])
def system_log_detail(request, log_id):
    """System log detail."""
    log = get_object_or_404(SystemLog, pk=log_id)
    
    context = {
        'log': log,
        'title': _('System Log Detail'),
    }
    return render(request, 'dashboard/system_log_detail.html', context)


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def clear_system_logs(request):
    """Clear system logs."""
    # Get date range
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    if start_date and end_date:
        SystemLog.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).delete()
    else:
        # Clear all logs older than 30 days
        SystemLog.objects.filter(
            created_at__lt=timezone.now() - timezone.timedelta(days=30)
        ).delete()
    
    messages.success(request, _('System logs cleared.'))
    return redirect('dashboard:system_log_list')


# ==================== AJAX VIEWS ====================

@login_required
@require_http_methods(["GET"])
def get_dashboard_stats_ajax(request):
    """Get dashboard statistics via AJAX."""
    stats = get_dashboard_statistics(request.user)
    
    return JsonResponse({
        'sales': stats['sales'],
        'orders': stats['orders'],
        'products': stats['products'],
        'customers': stats['customers'],
        'reviews': stats['reviews'],
        'support': stats['support'],
        'payments': stats['payments'],
        'ads': stats['ads'],
    })


@login_required
@require_http_methods(["GET"])
def get_recent_activity_ajax(request):
    """Get recent activity via AJAX."""
    activity = get_recent_activity(request.user)
    
    data = {
        'recent_orders': [
            {
                'id': str(order.id),
                'order_number': order.order_number,
                'customer': order.user.get_full_name() or order.user.username,
                'status': order.status,
                'total': order.total_amount,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for order in activity['recent_orders']
        ],
        'recent_products': [
            {
                'id': str(product.id),
                'name': product.name,
                'price': product.get_price(),
                'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for product in activity['recent_products']
        ],
        'recent_customers': [
            {
                'id': str(customer.id),
                'name': customer.get_full_name() or customer.username,
                'email': customer.email,
                'joined_at': customer.date_joined.strftime('%Y-%m-%d'),
            }
            for customer in activity['recent_customers']
        ],
        'recent_reviews': [
            {
                'id': str(review.id),
                'product': review.product.name,
                'rating': review.overall_rating,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for review in activity['recent_reviews']
        ],
        'system_logs': [
            {
                'id': str(log.id),
                'action': log.action,
                'message': log.message,
                'level': log.level,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for log in activity['system_logs']
        ],
    }
    
    return JsonResponse(data)


@login_required
@require_http_methods(["GET"])
def get_sales_chart_data_ajax(request):
    """Get sales chart data via AJAX."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        start_date = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
    
    # Get sales by day
    sales_by_day = Order.objects.filter(
        status__in=['completed', 'delivered', 'paid'],
        created_at__date__range=[start_date, end_date]
    ).annotate(
        day=ExtractDay('created_at')
    ).values('day').annotate(
        total=Sum('total_amount')
    ).order_by('day')
    
    # Get orders by day
    orders_by_day = Order.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).annotate(
        day=ExtractDay('created_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Combine data
    chart_data = []
    all_days = set(sales_by_day.values_list('day', flat=True)) | set(orders_by_day.values_list('day', flat=True))
    
    for day in sorted(all_days):
        sales = next((item['total'] for item in sales_by_day if item['day'] == day), 0)
        orders = next((item['count'] for item in orders_by_day if item['day'] == day), 0)
        
        chart_data.append({
            'day': day,
            'sales': float(sales) if sales else 0,
            'orders': orders,
        })
    
    return JsonResponse({'chart_data': chart_data})


@login_required
@require_http_methods(["GET"])
def get_quick_actions_ajax(request):
    """Get quick actions via AJAX."""
    actions = QuickAction.objects.filter(is_active=True)
    
    actions_data = []
    for action in actions:
        actions_data.append({
            'id': str(action.id),
            'name': action.name,
            'url': action.url,
            'icon': action.icon,
            'color': action.color,
        })
    
    return JsonResponse({'actions': actions_data})


@login_required
@require_http_methods(["GET"])
def get_widget_data_ajax(request, widget_id):
    """Get widget data via AJAX."""
    widget = get_object_or_404(DashboardWidget, pk=widget_id)
    
    # Get data based on widget type
    if widget.widget_type == 'statistics':
        data = get_dashboard_statistics(request.user)
    elif widget.widget_type == 'recent_orders':
        data = get_recent_activity(request.user)['recent_orders']
    elif widget.widget_type == 'recent_products':
        data = get_recent_activity(request.user)['recent_products']
    elif widget.widget_type == 'recent_customers':
        data = get_recent_activity(request.user)['recent_customers']
    elif widget.widget_type == 'sales_chart':
        start_date = (timezone.now() - timezone.timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        sales_data = get_sales_chart_data_ajax(request)
        data = json.loads(sales_data.content)
    else:
        data = {}
    
    return JsonResponse({'data': data})
