"""
API URL Configuration
All API endpoints are defined here
"""

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

# Import all views
from api.views.core_views import (
    SiteSettingsViewSet,
    ThemeConfigViewSet,
    ContactViewSet,
    AdminNoteViewSet,
    SystemLogViewSet,
    CountryViewSet,
    CurrencyViewSet,
    SiteStatsAPIView,
    HealthCheckAPIView,
)

from api.views.dashboard_admin_views import (
    AdminDashboardViewSet,
    DashboardWidgetViewSet,
    AdminMenuViewSet,
    AdminMenuItemViewSet,
    AdminQuickActionViewSet,
    AdminSettingsViewSet,
    AdminUserSettingsViewSet,
    AdminActivityViewSet,
    DashboardStatsAPIView,
    AdminSettingsAPIView,
)

# Add dashboard_admin URLs to router
main_router.register(r'admin/dashboards', AdminDashboardViewSet, basename='admin-dashboard')
main_router.register(r'admin/widgets', DashboardWidgetViewSet, basename='dashboard-widget')
main_router.register(r'admin/menus', AdminMenuViewSet, basename='admin-menu')
main_router.register(r'admin/menu-items', AdminMenuItemViewSet, basename='admin-menu-item')
main_router.register(r'admin/quick-actions', AdminQuickActionViewSet, basename='admin-quick-action')
main_router.register(r'admin/settings', AdminSettingsViewSet, basename='admin-settings')
main_router.register(r'admin/user-settings', AdminUserSettingsViewSet, basename='admin-user-settings')
main_router.register(r'admin/activities', AdminActivityViewSet, basename='admin-activity')

from api.views.accounts_views import (
    UserViewSet,
    UserProfileViewSet,
    UserAddressViewSet,
    UserRegistrationAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    PasswordResetAPIView,
    PasswordResetConfirmAPIView,
    PasswordChangeAPIView,
    WishlistViewSet,
    UserStatsAPIView,
    UserMeAPIView,
)

from api.views.products_views import (
    CategoryViewSet,
    BrandViewSet,
    TagViewSet,
    AttributeViewSet,
    AttributeValueViewSet,
    ProductViewSet,
    ProductImageViewSet,
    ProductVariantViewSet,
    ProductSearchAPIView,
    ProductFilterAPIView,
    ProductStatsAPIView,
    CategoryTreeAPIView,
)

from api.views.cart_views import (
    CartViewSet,
    CartItemViewSet,
    AddToCartAPIView,
    UpdateCartItemAPIView,
    RemoveFromCartAPIView,
    ClearCartAPIView,
    ApplyCouponAPIView,
    RemoveCouponAPIView,
    CartSummaryAPIView,
)

from api.views.orders_views import (
    OrderViewSet,
    OrderItemViewSet,
    ShippingViewSet,
    OrderCreateAPIView,
    OrderUpdateAPIView,
    OrderStatusUpdateAPIView,
    OrderCancelAPIView,
    OrderRefundAPIView,
    OrderStatsAPIView,
    OrderExportAPIView,
)

from api.views.payments_views import (
    PaymentMethodViewSet,
    WalletViewSet,
    WalletTransactionViewSet,
    PaymentTransactionViewSet,
    RefundViewSet,
    PaymentVerifyAPIView,
    PaymentCallbackAPIView,
    PaymentStatsAPIView,
    PaymentGatewayConfigAPIView,
)

from api.views.shipping_views import (
    ShippingMethodViewSet,
    ShippingZoneViewSet,
    ShippingClassViewSet,
    PickupLocationViewSet,
    DeliveryTimeViewSet,
    ShippingRateViewSet,
    ShippingCalculatorAPIView,
    ShippingStatsAPIView,
)

from api.views.inventory_views import (
    SupplierViewSet,
    InventoryLocationViewSet,
    StockMovementViewSet,
    PurchaseOrderViewSet,
    InventoryViewSet,
    InventoryUpdateAPIView,
    StockAdjustmentAPIView,
    InventoryTransferAPIView,
    InventoryStatsAPIView,
)

from api.views.discounts_views import (
    PriceRuleViewSet,
    CouponViewSet,
    DiscountViewSet,
    CouponUsageViewSet,
    CouponValidateAPIView,
    DiscountCalculatorAPIView,
    DiscountStatsAPIView,
)

from api.views.reviews_views import (
    ReviewViewSet,
    ReviewImageViewSet,
    ReviewHelpfulnessViewSet,
    ReviewCreateAPIView,
    ReviewUpdateAPIView,
    ReviewModerationAPIView,
    ReviewStatsAPIView,
)

from api.views.support_views import (
    TicketCategoryViewSet,
    FAQCategoryViewSet,
    FAQViewSet,
    TicketViewSet,
    TicketMessageViewSet,
    TicketCreateAPIView,
    TicketStatusUpdateAPIView,
    SupportStatsAPIView,
)

from api.views.blog_views import (
    BlogCategoryViewSet,
    BlogTagViewSet,
    BlogPostViewSet,
    BlogCommentViewSet,
    BlogStatsAPIView,
)

from api.views.ads_views import (
    AdSpaceViewSet,
    AdBannerViewSet,
    AdImpressionViewSet,
    AdClickViewSet,
    AdImpressionCreateAPIView,
    AdClickCreateAPIView,
    AdStatsAPIView,
)

# Create routers
main_router = DefaultRouter()
simple_router = SimpleRouter()

# Core URLs
main_router.register(r'core/settings', SiteSettingsViewSet, basename='site-settings')
main_router.register(r'core/theme', ThemeConfigViewSet, basename='theme-config')
main_router.register(r'core/contacts', ContactViewSet, basename='contact')
main_router.register(r'core/admin-notes', AdminNoteViewSet, basename='admin-note')
main_router.register(r'core/system-logs', SystemLogViewSet, basename='system-log')
main_router.register(r'core/countries', CountryViewSet, basename='country')
main_router.register(r'core/currencies', CurrencyViewSet, basename='currency')

# Accounts URLs
main_router.register(r'accounts/users', UserViewSet, basename='user')
main_router.register(r'accounts/profiles', UserProfileViewSet, basename='user-profile')
main_router.register(r'accounts/addresses', UserAddressViewSet, basename='user-address')
main_router.register(r'accounts/wishlist', WishlistViewSet, basename='wishlist')

# Products URLs
main_router.register(r'products/categories', CategoryViewSet, basename='category')
main_router.register(r'products/brands', BrandViewSet, basename='brand')
main_router.register(r'products/tags', TagViewSet, basename='tag')
main_router.register(r'products/attributes', AttributeViewSet, basename='attribute')
main_router.register(r'products/attribute-values', AttributeValueViewSet, basename='attribute-value')
main_router.register(r'products', ProductViewSet, basename='product')
main_router.register(r'products/images', ProductImageViewSet, basename='product-image')
main_router.register(r'products/variants', ProductVariantViewSet, basename='product-variant')

# Cart URLs
main_router.register(r'cart', CartViewSet, basename='cart')
main_router.register(r'cart/items', CartItemViewSet, basename='cart-item')

# Orders URLs
main_router.register(r'orders', OrderViewSet, basename='order')
main_router.register(r'orders/items', OrderItemViewSet, basename='order-item')
main_router.register(r'orders/shipping', ShippingViewSet, basename='shipping')

# Payments URLs
main_router.register(r'payments/methods', PaymentMethodViewSet, basename='payment-method')
main_router.register(r'payments/wallets', WalletViewSet, basename='wallet')
main_router.register(r'payments/transactions', WalletTransactionViewSet, basename='wallet-transaction')
main_router.register(r'payments/payment-transactions', PaymentTransactionViewSet, basename='payment-transaction')
main_router.register(r'payments/refunds', RefundViewSet, basename='refund')

# Shipping URLs
main_router.register(r'shipping/methods', ShippingMethodViewSet, basename='shipping-method')
main_router.register(r'shipping/zones', ShippingZoneViewSet, basename='shipping-zone')
main_router.register(r'shipping/classes', ShippingClassViewSet, basename='shipping-class')
main_router.register(r'shipping/locations', PickupLocationViewSet, basename='pickup-location')
main_router.register(r'shipping/delivery-times', DeliveryTimeViewSet, basename='delivery-time')
main_router.register(r'shipping/rates', ShippingRateViewSet, basename='shipping-rate')

# Inventory URLs
main_router.register(r'inventory/suppliers', SupplierViewSet, basename='supplier')
main_router.register(r'inventory/locations', InventoryLocationViewSet, basename='inventory-location')
main_router.register(r'inventory/movements', StockMovementViewSet, basename='stock-movement')
main_router.register(r'inventory/purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
main_router.register(r'inventory', InventoryViewSet, basename='inventory')

# Discounts URLs
main_router.register(r'discounts/price-rules', PriceRuleViewSet, basename='price-rule')
main_router.register(r'discounts/coupons', CouponViewSet, basename='coupon')
main_router.register(r'discounts', DiscountViewSet, basename='discount')
main_router.register(r'discounts/usages', CouponUsageViewSet, basename='coupon-usage')

# Reviews URLs
main_router.register(r'reviews', ReviewViewSet, basename='review')
main_router.register(r'reviews/images', ReviewImageViewSet, basename='review-image')
main_router.register(r'reviews/helpfulness', ReviewHelpfulnessViewSet, basename='review-helpfulness')

# Support URLs
main_router.register(r'support/ticket-categories', TicketCategoryViewSet, basename='ticket-category')
main_router.register(r'support/faq-categories', FAQCategoryViewSet, basename='faq-category')
main_router.register(r'support/faqs', FAQViewSet, basename='faq')
main_router.register(r'support/tickets', TicketViewSet, basename='ticket')
main_router.register(r'support/messages', TicketMessageViewSet, basename='ticket-message')

# Blog URLs
main_router.register(r'blog/categories', BlogCategoryViewSet, basename='blog-category')
main_router.register(r'blog/tags', BlogTagViewSet, basename='blog-tag')
main_router.register(r'blog/posts', BlogPostViewSet, basename='blog-post')
main_router.register(r'blog/comments', BlogCommentViewSet, basename='blog-comment')

# Ads URLs
main_router.register(r'ads/spaces', AdSpaceViewSet, basename='ad-space')
main_router.register(r'ads/banners', AdBannerViewSet, basename='ad-banner')
main_router.register(r'ads/impressions', AdImpressionViewSet, basename='ad-impression')
main_router.register(r'ads/clicks', AdClickViewSet, basename='ad-click')

# API URL patterns
urlpatterns = [
    # Health check
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
    
    # Authentication
    path('auth/register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('auth/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('auth/logout/', UserLogoutAPIView.as_view(), name='user-logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/password-reset/', PasswordResetAPIView.as_view(), name='password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
    path('auth/password-change/', PasswordChangeAPIView.as_view(), name='password-change'),
    
    # Current user
    path('me/', UserMeAPIView.as_view(), name='user-me'),
    path('me/stats/', UserStatsAPIView.as_view(), name='user-stats'),
    
    # Products
    path('products/search/', ProductSearchAPIView.as_view(), name='product-search'),
    path('products/filter/', ProductFilterAPIView.as_view(), name='product-filter'),
    path('products/stats/', ProductStatsAPIView.as_view(), name='product-stats'),
    path('products/tree/', CategoryTreeAPIView.as_view(), name='category-tree'),
    
    # Cart
    path('cart/add/', AddToCartAPIView.as_view(), name='add-to-cart'),
    path('cart/update/', UpdateCartItemAPIView.as_view(), name='update-cart-item'),
    path('cart/remove/', RemoveFromCartAPIView.as_view(), name='remove-from-cart'),
    path('cart/clear/', ClearCartAPIView.as_view(), name='clear-cart'),
    path('cart/coupon/apply/', ApplyCouponAPIView.as_view(), name='apply-coupon'),
    path('cart/coupon/remove/', RemoveCouponAPIView.as_view(), name='remove-coupon'),
    path('cart/summary/', CartSummaryAPIView.as_view(), name='cart-summary'),
    
    # Orders
    path('orders/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/update/', OrderUpdateAPIView.as_view(), name='order-update'),
    path('orders/<int:pk>/status/', OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path('orders/<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='order-cancel'),
    path('orders/<int:pk>/refund/', OrderRefundAPIView.as_view(), name='order-refund'),
    path('orders/stats/', OrderStatsAPIView.as_view(), name='order-stats'),
    path('orders/export/', OrderExportAPIView.as_view(), name='order-export'),
    
    # Payments
    path('payments/verify/', PaymentVerifyAPIView.as_view(), name='payment-verify'),
    path('payments/callback/', PaymentCallbackAPIView.as_view(), name='payment-callback'),
    path('payments/stats/', PaymentStatsAPIView.as_view(), name='payment-stats'),
    path('payments/gateway-config/', PaymentGatewayConfigAPIView.as_view(), name='payment-gateway-config'),
    
    # Shipping
    path('shipping/calculate/', ShippingCalculatorAPIView.as_view(), name='shipping-calculate'),
    path('shipping/stats/', ShippingStatsAPIView.as_view(), name='shipping-stats'),
    
    # Inventory
    path('inventory/<int:pk>/update/', InventoryUpdateAPIView.as_view(), name='inventory-update'),
    path('inventory/stock-adjustment/', StockAdjustmentAPIView.as_view(), name='stock-adjustment'),
    path('inventory/transfer/', InventoryTransferAPIView.as_view(), name='inventory-transfer'),
    path('inventory/stats/', InventoryStatsAPIView.as_view(), name='inventory-stats'),
    
    # Discounts
    path('discounts/coupons/validate/', CouponValidateAPIView.as_view(), name='coupon-validate'),
    path('discounts/calculate/', DiscountCalculatorAPIView.as_view(), name='discount-calculate'),
    path('discounts/stats/', DiscountStatsAPIView.as_view(), name='discount-stats'),
    
    # Reviews
    path('reviews/create/', ReviewCreateAPIView.as_view(), name='review-create'),
    path('reviews/<int:pk>/update/', ReviewUpdateAPIView.as_view(), name='review-update'),
    path('reviews/<int:pk>/moderate/', ReviewModerationAPIView.as_view(), name='review-moderate'),
    path('reviews/stats/', ReviewStatsAPIView.as_view(), name='review-stats'),
    
    # Support
    path('support/tickets/create/', TicketCreateAPIView.as_view(), name='ticket-create'),
    path('support/tickets/<int:pk>/status/', TicketStatusUpdateAPIView.as_view(), name='ticket-status-update'),
    path('support/stats/', SupportStatsAPIView.as_view(), name='support-stats'),
    
    # Blog
    path('blog/stats/', BlogStatsAPIView.as_view(), name='blog-stats'),
    
    # Ads
    path('ads/impressions/', AdImpressionCreateAPIView.as_view(), name='ad-impression-create'),
    path('ads/clicks/', AdClickCreateAPIView.as_view(), name='ad-click-create'),
    path('ads/stats/', AdStatsAPIView.as_view(), name='ad-stats'),
    
    # Site stats
    path('stats/', SiteStatsAPIView.as_view(), name='site-stats'),
    
    # Admin dashboard stats
    path('admin/stats/', DashboardStatsAPIView.as_view({'get': 'list'}), name='admin-dashboard-stats'),
    path('admin/settings/', AdminSettingsAPIView.as_view({'get': 'get', 'post': 'post'}), name='admin-settings'),
    
    # Include router URLs
    path('', include(main_router.urls)),
]

# Add trailing slash for all URLs
urlpatterns = [
    re_path(r'^(?P<url>.*)[^/]$', re_path(r'^(?P<url>.*)$', include(urlpatterns))),
] + urlpatterns
