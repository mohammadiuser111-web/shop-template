"""
Admin configuration for dashboard_admin app.
Custom admin panel registration and customization.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import HttpResponseRedirect

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


# Custom Admin Site
class CustomAdminSite(AdminSite):
    """Custom admin site with Persian branding and customizations."""
    
    site_header = _('پنل مدیریت فروشگاه')
    site_title = _('پنل مدیریت')
    index_title = _('داشبورد مدیریت')
    
    def get_app_list(self, request):
        """Customize app list ordering and visibility."""
        app_list = super().get_app_list(request)
        
        # Custom ordering for apps
        app_order = [
            'dashboard_admin',
            'products', 
            'orders',
            'accounts',
            'payments',
            'shipping',
            'discounts',
            'inventory',
            'cart',
            'ads',
            'blog',
            'reviews',
            'support',
            'notifications',
            'core',
        ]
        
        def get_app_priority(app):
            app_label = app.get('app_label', '')
            try:
                return app_order.index(app_label)
            except ValueError:
                return len(app_order)
        
        app_list.sort(key=get_app_priority)
        return app_list
    
    def login(self, request, extra_context=None):
        """Custom login page redirect."""
        if request.method == 'GET' and request.user.is_authenticated:
            return HttpResponseRedirect(reverse('admin:index'))
        return super().login(request, extra_context)


# Register custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')


@admin.register(AdminDashboard)
class AdminDashboardAdmin(admin.ModelAdmin):
    """Admin configuration for AdminDashboard model."""
    list_display = ('name', 'code', 'is_default', 'is_active', 'created_at')
    list_filter = ('is_default', 'is_active')
    search_fields = ('name', 'code', 'description')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('name', 'code', 'description')
        }),
        (_('تنظیمات Layout'), {
            'fields': ('layout',)
        }),
        (_('وضعیت'), {
            'fields': ('is_default', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        """Ensure only one default dashboard."""
        if obj.is_default:
            AdminDashboard.objects.filter(is_default=True).exclude(pk=obj.pk).update(is_default=False)
        super().save_model(request, obj, form, change)


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """Admin configuration for DashboardWidget model."""
    list_display = ('name', 'code', 'widget_type', 'chart_type', 'sort_order', 'is_active')
    list_filter = ('widget_type', 'is_active')
    search_fields = ('name', 'code', 'title')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('name', 'code', 'widget_type')
        }),
        (_('تنظیمات Chart'), {
            'fields': ('chart_type', 'config')
        }),
        (_('نمایش'), {
            'fields': ('title', 'icon', 'color', 'width', 'height')
        }),
        (_('وضعیت'), {
            'fields': ('sort_order', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdminMenu)
class AdminMenuAdmin(admin.ModelAdmin):
    """Admin configuration for AdminMenu model."""
    list_display = ('name', 'menu_type', 'sort_order', 'is_active')
    list_filter = ('menu_type', 'is_active')
    search_fields = ('name',)
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('name', 'menu_type')
        }),
        (_('آیتم‌های منو'), {
            'fields': ('items',)
        }),
        (_('وضعیت'), {
            'fields': ('sort_order', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdminMenuItem)
class AdminMenuItemAdmin(admin.ModelAdmin):
    """Admin configuration for AdminMenuItem model."""
    list_display = ('title', 'menu', 'parent', 'item_type', 'sort_order', 'is_visible')
    list_filter = ('item_type', 'menu', 'is_visible')
    search_fields = ('title', 'url')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('menu', 'parent', 'item_type')
        }),
        (_('نمایش'), {
            'fields': ('title', 'icon', 'color')
        }),
        (_('لینک'), {
            'fields': ('url', 'target')
        }),
        (_('دسترسی'), {
            'fields': ('required_permission',)
        }),
        (_('وضعیت'), {
            'fields': ('sort_order', 'is_visible')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdminQuickAction)
class AdminQuickActionAdmin(admin.ModelAdmin):
    """Admin configuration for AdminQuickAction model."""
    list_display = ('title', 'code', 'action_type', 'sort_order', 'is_active')
    list_filter = ('action_type', 'is_active')
    search_fields = ('name', 'code', 'title')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('name', 'code', 'action_type')
        }),
        (_('تنظیمات'), {
            'fields': ('action_config',)
        }),
        (_('نمایش'), {
            'fields': ('title', 'icon', 'color')
        }),
        (_('دسترسی'), {
            'fields': ('required_permission',)
        }),
        (_('وضعیت'), {
            'fields': ('sort_order', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdminSettings)
class AdminSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for AdminSettings model (Singleton)."""
    list_display = ('id', 'language', 'theme_color', 'sidebar_color')
    fieldsets = (
        (_('برندینگ'), {
            'fields': ('logo', 'logo_small', 'favicon')
        }),
        (_('تم'), {
            'fields': ('theme_color', 'sidebar_color', 'sidebar_text_color')
        }),
        (_('Layout'), {
            'fields': ('sidebar_collapsed', 'layout')
        }),
        (_('زبان'), {
            'fields': ('language',)
        }),
        (_('اعلان‌ها'), {
            'fields': ('show_notifications',)
        }),
        (_('داشبورد پیش‌فرض'), {
            'fields': ('default_dashboard',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        """Prevent adding multiple instances (singleton)."""
        return not AdminSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of singleton."""
        return False


@admin.register(AdminUserSettings)
class AdminUserSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for AdminUserSettings model."""
    list_display = ('user', 'theme', 'language', 'sidebar_collapsed')
    list_filter = ('theme', 'language')
    search_fields = ('user__username', 'user__email')
    fieldsets = (
        (_('کاربر'), {
            'fields': ('user',)
        }),
        (_('تم'), {
            'fields': ('theme',)
        }),
        (_('زبان'), {
            'fields': ('language',)
        }),
        (_('Layout'), {
            'fields': ('sidebar_collapsed',)
        }),
        (_('اعلان‌ها'), {
            'fields': ('email_notifications', 'push_notifications')
        }),
        (_('داشبورد'), {
            'fields': ('dashboard',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdminActivity)
class AdminActivityAdmin(admin.ModelAdmin):
    """Admin configuration for AdminActivity model."""
    list_display = ('user', 'action', 'model_name', 'object_repr', 'created_at')
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('user__username', 'model_name', 'object_repr', 'description', 'ip_address')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('user', 'action', 'model_name', 'object_id', 'object_repr')
        }),
        (_('جزئیات'), {
            'fields': ('description', 'changes')
        }),
        (_('محیط'), {
            'fields': ('ip_address', 'user_agent')
        }),
    )
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        """Prevent manual addition of activities."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent manual modification of activities."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of activities."""
        return request.user.is_superuser
