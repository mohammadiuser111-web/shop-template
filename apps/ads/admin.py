"""
Admin configuration for ads app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import AdSlot, Advertisement, AdImpression, AdClick


@admin.register(AdSlot)
class AdSlotAdmin(admin.ModelAdmin):
    """Admin configuration for AdSlot model."""
    list_display = ('name', 'code', 'width', 'height', 'is_responsive', 'is_active', 'created_at')
    list_filter = ('is_responsive', 'is_active')
    search_fields = ('name', 'code', 'description')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('name', 'code', 'description')
        }),
        (_('ابعاد'), {
            'fields': ('width', 'height', 'is_responsive')
        }),
        (_('وضعیت'), {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch."""
        return super().get_queryset(request).prefetch_related('ads')


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    """Admin configuration for Advertisement model."""
    list_display = (
        'name', 'slot', 'ad_type', 'priority', 'is_active', 
        'start_date', 'end_date', 'get_impressions', 'get_clicks', 'get_ctr'
    )
    list_filter = ('slot', 'ad_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('name', 'title', 'description', 'url')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('name', 'slot', 'priority', 'is_active')
        }),
        (_('محتوا'), {
            'fields': ('ad_type', 'image', 'image_alt', 'html_content', 'script_content', 'video_url', 'video_embed_code')
        }),
        (_('لینک'), {
            'fields': ('url', 'target')
        }),
        (_('نمایش'), {
            'fields': ('title', 'description')
        }),
        (_('زمان‌بندی'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('آمار'), {
            'fields': ('impression_count', 'click_count')
        }),
        (_('کاربر'), {
            'fields': ('created_by',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'impression_count', 'click_count')
    
    def get_impressions(self, obj):
        """Get impression count."""
        return obj.impression_count
    get_impressions.short_description = _('نمایش')
    
    def get_clicks(self, obj):
        """Get click count."""
        return obj.click_count
    get_clicks.short_description = _('کلیک')
    
    def get_ctr(self, obj):
        """Get CTR percentage."""
        ctr = obj.get_ctr()
        return f"{ctr:.2f}%"
    get_ctr.short_description = _('CTR')
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('slot', 'created_by')


@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    """Admin configuration for AdImpression model."""
    list_display = ('ad', 'user', 'ip_address', 'created_at')
    list_filter = ('ad', 'created_at')
    search_fields = ('ad__name', 'user__username', 'ip_address')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('ad', 'user', 'ip_address', 'user_agent', 'referrer')
        }),
    )
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        """Prevent manual addition."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent manual modification."""
        return False
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('ad', 'user')


@admin.register(AdClick)
class AdClickAdmin(admin.ModelAdmin):
    """Admin configuration for AdClick model."""
    list_display = ('ad', 'user', 'impression', 'ip_address', 'created_at')
    list_filter = ('ad', 'created_at')
    search_fields = ('ad__name', 'user__username', 'ip_address')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('ad', 'impression', 'user', 'ip_address', 'user_agent', 'referrer')
        }),
    )
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        """Prevent manual addition."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent manual modification."""
        return False
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('ad', 'impression', 'user')
