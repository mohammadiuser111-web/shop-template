"""
Admin configuration for payments app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PaymentGateway, Transaction, Wallet, WalletTransaction


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentGateway model."""
    list_display = ('title', 'gateway_type', 'is_active', 'sort_order', 'created_at')
    list_filter = ('gateway_type', 'is_active')
    search_fields = ('name', 'title', 'description')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('name', 'gateway_type', 'title', 'description')
        }),
        (_('تنظیمات'), {
            'fields': ('config', 'logo', 'is_active', 'sort_order')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on gateway type."""
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.gateway_type:
            # Could customize form fields based on gateway type
            pass
        return form


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for Transaction model."""
    list_display = (
        'transaction_id', 'user', 'order', 'gateway', 'amount', 
        'currency', 'status', 'transaction_type', 'created_at'
    )
    list_filter = ('status', 'transaction_type', 'gateway', 'created_at')
    search_fields = (
        'transaction_id', 'gateway_reference', 'user__username', 
        'user__email', 'customer_name', 'customer_email', 'customer_phone'
    )
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('transaction_id', 'transaction_type', 'amount', 'currency')
        }),
        (_('ارتباط‌ها'), {
            'fields': ('user', 'order', 'refund', 'gateway')
        }),
        (_('وضعیت'), {
            'fields': ('status', 'gateway_reference')
        }),
        (_('پاسخ درگاه'), {
            'fields': ('gateway_response',)
        }),
        (_('اطلاعات مشتری'), {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        (_('خطا'), {
            'fields': ('error_code', 'error_message')
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    
    actions = ['mark_as_success', 'mark_as_failed', 'mark_as_cancelled']
    
    def mark_as_success(self, request, queryset):
        """Mark selected transactions as success."""
        count = queryset.update(status='success', completed_at=timezone.now())
        self.message_user(request, f"{count} تراکنش با موفقیت علامت‌دار شد.")
    
    def mark_as_failed(self, request, queryset):
        """Mark selected transactions as failed."""
        count = queryset.update(status='failed')
        self.message_user(request, f"{count} تراکنش به عنوان ناموفق علامت‌دار شد.")
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected transactions as cancelled."""
        count = queryset.update(status='cancelled')
        self.message_user(request, f"{count} تراکنش به عنوان لغو شده علامت‌دار شد.")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Admin configuration for Wallet model."""
    list_display = ('user', 'balance', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('user', 'balance')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        """Prevent manual wallet creation."""
        return False


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    """Admin configuration for WalletTransaction model."""
    list_display = ('wallet', 'amount', 'transaction_type', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('wallet__user__username', 'description')
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('wallet', 'amount', 'transaction_type')
        }),
        (_('جزئیات'), {
            'fields': ('balance_after', 'description', 'transaction')
        }),
    )
    readonly_fields = ('created_at',)
