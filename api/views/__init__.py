"""
API Views Package
Centralized imports for all view modules
"""

# Core views
from .core_views import (
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

# Accounts views
from .accounts_views import (
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

# Products views
from .products_views import (
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

# Cart views
from .cart_views import (
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

# Orders views
from .orders_views import (
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

# Payments views
from .payments_views import (
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

# Shipping views
from .shipping_views import (
    ShippingMethodViewSet,
    ShippingZoneViewSet,
    ShippingClassViewSet,
    PickupLocationViewSet,
    DeliveryTimeViewSet,
    ShippingRateViewSet,
    ShippingCalculatorAPIView,
    ShippingStatsAPIView,
)

# Inventory views
from .inventory_views import (
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

# Discounts views
from .discounts_views import (
    PriceRuleViewSet,
    CouponViewSet,
    DiscountViewSet,
    CouponUsageViewSet,
    CouponValidateAPIView,
    DiscountCalculatorAPIView,
    DiscountStatsAPIView,
)

# Reviews views
from .reviews_views import (
    ReviewViewSet,
    ReviewImageViewSet,
    ReviewHelpfulnessViewSet,
    ReviewCreateAPIView,
    ReviewUpdateAPIView,
    ReviewModerationAPIView,
    ReviewStatsAPIView,
)

# Support views
from .support_views import (
    TicketCategoryViewSet,
    FAQCategoryViewSet,
    FAQViewSet,
    TicketViewSet,
    TicketMessageViewSet,
    TicketCreateAPIView,
    TicketStatusUpdateAPIView,
    SupportStatsAPIView,
)

# Blog views
from .blog_views import (
    BlogCategoryViewSet,
    BlogTagViewSet,
    BlogPostViewSet,
    BlogCommentViewSet,
    BlogStatsAPIView,
)

# Ads views
from .ads_views import (
    AdSpaceViewSet,
    AdBannerViewSet,
    AdImpressionViewSet,
    AdClickViewSet,
    AdImpressionCreateAPIView,
    AdClickCreateAPIView,
    AdStatsAPIView,
)

__all__ = [
    # Core
    'SiteSettingsViewSet', 'ThemeConfigViewSet', 'ContactViewSet',
    'AdminNoteViewSet', 'SystemLogViewSet', 'CountryViewSet',
    'CurrencyViewSet', 'SiteStatsAPIView', 'HealthCheckAPIView',
    
    # Accounts
    'UserViewSet', 'UserProfileViewSet', 'UserAddressViewSet',
    'UserRegistrationAPIView', 'UserLoginAPIView', 'UserLogoutAPIView',
    'PasswordResetAPIView', 'PasswordResetConfirmAPIView', 'PasswordChangeAPIView',
    'WishlistViewSet', 'UserStatsAPIView', 'UserMeAPIView',
    
    # Products
    'CategoryViewSet', 'BrandViewSet', 'TagViewSet',
    'AttributeViewSet', 'AttributeValueViewSet', 'ProductViewSet',
    'ProductImageViewSet', 'ProductVariantViewSet', 'ProductSearchAPIView',
    'ProductFilterAPIView', 'ProductStatsAPIView', 'CategoryTreeAPIView',
    
    # Cart
    'CartViewSet', 'CartItemViewSet', 'AddToCartAPIView',
    'UpdateCartItemAPIView', 'RemoveFromCartAPIView', 'ClearCartAPIView',
    'ApplyCouponAPIView', 'RemoveCouponAPIView', 'CartSummaryAPIView',
    
    # Orders
    'OrderViewSet', 'OrderItemViewSet', 'ShippingViewSet',
    'OrderCreateAPIView', 'OrderUpdateAPIView', 'OrderStatusUpdateAPIView',
    'OrderCancelAPIView', 'OrderRefundAPIView', 'OrderStatsAPIView',
    'OrderExportAPIView',
    
    # Payments
    'PaymentMethodViewSet', 'WalletViewSet', 'WalletTransactionViewSet',
    'PaymentTransactionViewSet', 'RefundViewSet', 'PaymentVerifyAPIView',
    'PaymentCallbackAPIView', 'PaymentStatsAPIView', 'PaymentGatewayConfigAPIView',
    
    # Shipping
    'ShippingMethodViewSet', 'ShippingZoneViewSet', 'ShippingClassViewSet',
    'PickupLocationViewSet', 'DeliveryTimeViewSet', 'ShippingRateViewSet',
    'ShippingCalculatorAPIView', 'ShippingStatsAPIView',
    
    # Inventory
    'SupplierViewSet', 'InventoryLocationViewSet', 'StockMovementViewSet',
    'PurchaseOrderViewSet', 'InventoryViewSet', 'InventoryUpdateAPIView',
    'StockAdjustmentAPIView', 'InventoryTransferAPIView', 'InventoryStatsAPIView',
    
    # Discounts
    'PriceRuleViewSet', 'CouponViewSet', 'DiscountViewSet',
    'CouponUsageViewSet', 'CouponValidateAPIView', 'DiscountCalculatorAPIView',
    'DiscountStatsAPIView',
    
    # Reviews
    'ReviewViewSet', 'ReviewImageViewSet', 'ReviewHelpfulnessViewSet',
    'ReviewCreateAPIView', 'ReviewUpdateAPIView', 'ReviewModerationAPIView',
    'ReviewStatsAPIView',
    
    # Support
    'TicketCategoryViewSet', 'FAQCategoryViewSet', 'FAQViewSet',
    'TicketViewSet', 'TicketMessageViewSet', 'TicketCreateAPIView',
    'TicketStatusUpdateAPIView', 'SupportStatsAPIView',
    
    # Blog
    'BlogCategoryViewSet', 'BlogTagViewSet', 'BlogPostViewSet',
    'BlogCommentViewSet', 'BlogStatsAPIView',
    
    # Ads
    'AdSpaceViewSet', 'AdBannerViewSet', 'AdImpressionViewSet',
    'AdClickViewSet', 'AdImpressionCreateAPIView', 'AdClickCreateAPIView',
    'AdStatsAPIView',
]
