"""
Views for dashboard_admin app.
Custom admin dashboard views and functionality.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.serializers import serialize
import json

from .models import (
    AdminDashboard,
    DashboardWidget,
    AdminMenu,
    AdminMenuItem,
    AdminQuickAction,
    AdminSettings,
    AdminUserSettings,
    AdminActivity,
)
from apps.products.models import Product, Category, Brand
from apps.orders.models import Order
from apps.accounts.models import User
from apps.payments.models import Transaction


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure user is admin."""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, 'شما به این صفحه دسترسی ندارید.')
        return redirect('store:home')


class DashboardView(AdminRequiredMixin, View):
    """Main admin dashboard view."""
    
    template_name = 'admin_panel/dashboard.html'
    
    def get(self, request):
        # Get user settings
        user_settings, created = AdminUserSettings.objects.get_or_create(user=request.user)
        
        # Get default dashboard
        settings = AdminSettings.get_instance()
        dashboard = settings.default_dashboard if settings else None
        if not dashboard:
            dashboard = AdminDashboard.objects.filter(is_default=True).first()
        if not dashboard:
            dashboard = AdminDashboard.objects.first()
        
        # Get widgets for this dashboard
        widgets = DashboardWidget.objects.filter(is_active=True).order_by('sort_order')
        
        # Get statistics
        stats = self.get_dashboard_stats()
        
        # Get recent activities
        activities = AdminActivity.objects.filter(user=request.user).order_by('-created_at')[:10]
        
        context = {
            'dashboard': dashboard,
            'widgets': widgets,
            'stats': stats,
            'activities': activities,
            'user_settings': user_settings,
            'page_title': 'داشبورد مدیریت',
        }
        
        return render(request, self.template_name, context)
    
    def get_dashboard_stats(self):
        """Calculate dashboard statistics."""
        today = timezone.now().date()
        
        # Product stats
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        out_of_stock = Product.objects.filter(inventory__quantity__lte=0).count()
        
        # Order stats
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        completed_orders = Order.objects.filter(status='completed').count()
        today_orders = Order.objects.filter(created_at__date=today).count()
        
        # User stats
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        today_users = User.objects.filter(date_joined__date=today).count()
        
        # Payment stats
        total_payments = Transaction.objects.count()
        successful_payments = Transaction.objects.filter(status='success').count()
        today_payments = Transaction.objects.filter(created_at__date=today).count()
        
        # Revenue
        total_revenue = Order.objects.filter(status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        today_revenue = Order.objects.filter(
            status='completed',
            created_at__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        return {
            'products': {
                'total': total_products,
                'active': active_products,
                'out_of_stock': out_of_stock,
            },
            'orders': {
                'total': total_orders,
                'pending': pending_orders,
                'completed': completed_orders,
                'today': today_orders,
            },
            'users': {
                'total': total_users,
                'active': active_users,
                'staff': staff_users,
                'today': today_users,
            },
            'payments': {
                'total': total_payments,
                'successful': successful_payments,
                'today': today_payments,
            },
            'revenue': {
                'total': total_revenue,
                'today': today_revenue,
            }
        }


class DashboardSettingsView(AdminRequiredMixin, View):
    """Dashboard settings view."""
    
    template_name = 'admin_panel/settings.html'
    
    def get(self, request):
        settings, created = AdminUserSettings.objects.get_or_create(user=request.user)
        global_settings = AdminSettings.get_instance()
        
        context = {
            'user_settings': settings,
            'global_settings': global_settings,
            'page_title': 'تنظیمات پنل مدیریت',
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        user_settings = AdminUserSettings.objects.get(user=request.user)
        
        # Update user settings
        user_settings.theme = request.POST.get('theme', user_settings.theme)
        user_settings.language = request.POST.get('language', user_settings.language)
        user_settings.sidebar_collapsed = request.POST.get('sidebar_collapsed', 'false').lower() == 'true'
        user_settings.email_notifications = request.POST.get('email_notifications', 'false').lower() == 'true'
        user_settings.push_notifications = request.POST.get('push_notifications', 'false').lower() == 'true'
        user_settings.save()
        
        messages.success(request, 'تنظیمات با موفقیت ذخیره شد.')
        return redirect('dashboard_admin:settings')


class WidgetDataView(AdminRequiredMixin, View):
    """API endpoint to get widget data."""
    
    def get(self, request, widget_id):
        widget = get_object_or_404(DashboardWidget, id=widget_id, is_active=True)
        
        data = self.get_widget_data(widget)
        
        return JsonResponse({
            'success': True,
            'data': data,
            'widget': {
                'id': widget.id,
                'name': widget.name,
                'title': widget.title,
                'type': widget.widget_type,
                'chart_type': widget.chart_type,
                'config': widget.config,
            }
        })
    
    def get_widget_data(self, widget):
        """Get data for a specific widget type."""
        widget_type = widget.widget_type
        
        if widget_type == 'chart':
            return self.get_chart_data(widget)
        elif widget_type == 'statistic':
            return self.get_statistic_data(widget)
        elif widget_type == 'list':
            return self.get_list_data(widget)
        elif widget_type == 'card':
            return self.get_card_data(widget)
        
        return {}
    
    def get_chart_data(self, widget):
        """Get data for chart widgets."""
        chart_type = widget.chart_type
        config = widget.config
        
        # Default: sales chart
        if 'data_source' in config:
            source = config['data_source']
            
            if source == 'sales_by_day':
                return self.get_sales_by_day_data(config)
            elif source == 'sales_by_category':
                return self.get_sales_by_category_data(config)
            elif source == 'orders_by_status':
                return self.get_orders_by_status_data(config)
        
        # Default sales by day
        return self.get_sales_by_day_data({})
    
    def get_sales_by_day_data(self, config):
        """Get sales data by day."""
        days = config.get('days', 30)
        
        from django.db.models.functions import TruncDate
        from django.db.models import Sum
        
        sales_data = Order.objects.filter(
            status='completed',
            created_at__gte=timezone.now() - timezone.timedelta(days=days)
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Sum('total_amount')
        ).order_by('date')
        
        return {
            'labels': [item['date'].strftime('%Y-%m-%d') for item in sales_data],
            'datasets': [{
                'label': 'فروش (تومان)',
                'data': [float(item['total'] or 0) for item in sales_data],
                'borderColor': '#2563eb',
                'backgroundColor': 'rgba(37, 99, 235, 0.1)',
            }]
        }
    
    def get_sales_by_category_data(self, config):
        """Get sales data by category."""
        from django.db.models import Sum
        
        sales_data = Order.objects.filter(status='completed').values('items__product__category__name').annotate(
            total=Sum('items__total_price')
        ).order_by('-total')[:10]
        
        return {
            'labels': [item['items__product__category__name'] or 'بدون دسته' for item in sales_data],
            'datasets': [{
                'label': 'فروش (تومان)',
                'data': [float(item['total'] or 0) for item in sales_data],
                'backgroundColor': [
                    '#2563eb', '#7c3aed', '#10b981', '#f59e0b', '#ef4444',
                    '#3b82f6', '#8b5cf6', '#06b6d4', '#f97316', '#eab308'
                ],
            }]
        }
    
    def get_orders_by_status_data(self, config):
        """Get orders by status."""
        from apps.orders.models import Order
        
        status_counts = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        status_labels = {
            'pending': 'در انتظار',
            'processing': 'در حال پردازش',
            'shipped': 'ارسال شده',
            'delivered': 'تحویل داده شده',
            'completed': 'تکمیل شده',
            'cancelled': 'لغو شده',
            'refunded': 'استرداد شده',
        }
        
        return {
            'labels': [status_labels.get(item['status'], item['status']) for item in status_counts],
            'datasets': [{
                'label': 'تعداد سفارشات',
                'data': [item['count'] for item in status_counts],
                'backgroundColor': [
                    '#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e',
                    '#10b981', '#06b6d4', '#3b82f6'
                ],
            }]
        }
    
    def get_statistic_data(self, widget):
        """Get data for statistic widgets."""
        config = widget.config
        stat_type = config.get('type', 'total_sales')
        
        if stat_type == 'total_sales':
            value = Order.objects.filter(status='completed').aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            return {'value': float(value), 'label': 'کل فروش'}
        
        elif stat_type == 'total_orders':
            value = Order.objects.count()
            return {'value': value, 'label': 'کل سفارشات'}
        
        elif stat_type == 'total_products':
            value = Product.objects.count()
            return {'value': value, 'label': 'کل محصولات'}
        
        elif stat_type == 'total_users':
            value = User.objects.count()
            return {'value': value, 'label': 'کل کاربران'}
        
        return {'value': 0, 'label': 'آمار'}
    
    def get_list_data(self, widget):
        """Get data for list widgets."""
        config = widget.config
        list_type = config.get('type', 'recent_orders')
        limit = config.get('limit', 5)
        
        if list_type == 'recent_orders':
            orders = Order.objects.filter(status='completed').order_by('-created_at')[:limit]
            data = []
            for order in orders:
                data.append({
                    'id': order.id,
                    'code': order.code,
                    'customer': order.user.get_full_name() if order.user else 'مهمان',
                    'total': float(order.total_amount),
                    'date': order.created_at.strftime('%Y-%m-%d %H:%M'),
                    'status': order.get_status_display(),
                })
            return {'items': data}
        
        elif list_type == 'recent_products':
            products = Product.objects.filter(is_active=True).order_by('-created_at')[:limit]
            data = []
            for product in products:
                data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'stock': product.inventory.quantity if hasattr(product, 'inventory') else 0,
                })
            return {'items': data}
        
        return {'items': []}
    
    def get_card_data(self, widget):
        """Get data for card widgets."""
        config = widget.config
        return config.get('data', {})


class ActivityLogView(AdminRequiredMixin, ListView):
    """View to display admin activity logs."""
    
    model = AdminActivity
    template_name = 'admin_panel/notifications.html'
    context_object_name = 'activities'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user
        user_filter = self.request.GET.get('user')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)
        
        # Filter by action
        action_filter = self.request.GET.get('action')
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        
        # Filter by model
        model_filter = self.request.GET.get('model')
        if model_filter:
            queryset = queryset.filter(model_name__icontains=model_filter)
        
        # Filter by date
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'گزارش فعالیت‌ها'
        context['actions'] = AdminActivity.ACTION_TYPES
        return context


class MenuManagementView(AdminRequiredMixin, View):
    """View to manage admin menu."""
    
    template_name = 'admin_panel/settings.html'
    
    def get(self, request):
        menus = AdminMenu.objects.filter(is_active=True).order_by('sort_order')
        menu_items = AdminMenuItem.objects.filter(is_visible=True).order_by('sort_order')
        
        context = {
            'menus': menus,
            'menu_items': menu_items,
            'page_title': 'مدیریت منوهای ادمین',
        }
        
        return render(request, self.template_name, context)


# API Views for AJAX requests
class GetDashboardDataView(AdminRequiredMixin, View):
    """Get dashboard data via AJAX."""
    
    def get(self, request):
        stats = DashboardView().get_dashboard_stats()
        
        return JsonResponse({
            'success': True,
            'stats': stats,
        })


class UpdateWidgetOrderView(AdminRequiredMixin, View):
    """Update widget sort order via AJAX."""
    
    def post(self, request):
        widget_ids = request.POST.getlist('widget_ids[]')
        
        for index, widget_id in enumerate(widget_ids):
            try:
                widget = DashboardWidget.objects.get(id=widget_id)
                widget.sort_order = index
                widget.save()
            except DashboardWidget.DoesNotExist:
                pass
        
        return JsonResponse({'success': True})


class ToggleSidebarView(AdminRequiredMixin, View):
    """Toggle sidebar collapsed state via AJAX."""
    
    def post(self, request):
        user_settings, created = AdminUserSettings.objects.get_or_create(user=request.user)
        user_settings.sidebar_collapsed = not user_settings.sidebar_collapsed
        user_settings.save()
        
        return JsonResponse({
            'success': True,
            'collapsed': user_settings.sidebar_collapsed
        })
