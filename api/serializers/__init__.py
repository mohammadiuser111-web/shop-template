"""
API Serializers Package
Centralized imports for all serializers modules
"""

# Core serializers
from .core_serializers import (
    CountrySerializer,
    CountryListSerializer,
    CurrencySerializer,
    SiteSettingsSerializer,
    ThemeConfigSerializer,
    ContactSerializer,
    ContactListSerializer,
    AdminNoteSerializer,
    AdminNoteListSerializer,
    SystemLogSerializer,
    SystemLogListSerializer,
    SiteStatsSerializer,
    ThemeSerializer,
)

# Accounts serializers
from .accounts_serializers import (
    UserPublicSerializer,
    UserProfileSerializer,
    UserAddressSerializer,
    UserAddressListSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserPasswordUpdateSerializer,
    UserPasswordResetSerializer,
    UserPasswordResetConfirmSerializer,
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    SocialLoginSerializer,
    WishlistSerializer,
    WishlistListSerializer,
    WishlistCreateSerializer,
    WishlistRemoveSerializer,
    UserStatsSerializer,
)

# Products serializers
from .products_serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CategoryTreeSerializer,
    BrandSerializer,
    BrandListSerializer,
    TagSerializer,
    AttributeSerializer,
    AttributeListSerializer,
    AttributeValueSerializer,
    AttributeValueListSerializer,
    ProductImageSerializer,
    ProductVariantSerializer,
    ProductVariantListSerializer,
    ProductReviewSerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
    ProductVariantCreateSerializer,
    ProductVariantUpdateSerializer,
    ProductSearchSerializer,
    ProductFilterSerializer,
    ProductStatsSerializer,
)

# Cart serializers
from .cart_serializers import (
    CartItemSerializer,
    CartItemListSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
    CartSerializer,
    CartListSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    RemoveFromCartSerializer,
    ClearCartSerializer,
    ApplyCouponSerializer,
    RemoveCouponSerializer,
    CartSummarySerializer,
)

# Orders serializers
from .orders_serializers import (
    OrderItemSerializer,
    OrderItemListSerializer,
    ShippingSerializer,
    ShippingListSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    OrderStatusUpdateSerializer,
    OrderCancelSerializer,
    OrderRefundSerializer,
    OrderStatsSerializer,
    OrderExportSerializer,
)

# Payments serializers
from .payments_serializers import (
    PaymentMethodSerializer,
    PaymentMethodListSerializer,
    WalletSerializer,
    WalletTransactionSerializer,
    WalletTransactionListSerializer,
    RefundSerializer,
    RefundListSerializer,
    PaymentTransactionSerializer,
    PaymentTransactionListSerializer,
    PaymentTransactionCreateSerializer,
    PaymentVerifySerializer,
    PaymentCallbackSerializer,
    PaymentStatsSerializer,
    PaymentGatewayConfigSerializer,
)

# Shipping serializers
from .shipping_serializers import (
    ShippingZoneSerializer,
    ShippingClassSerializer,
    PickupLocationSerializer,
    DeliveryTimeSerializer,
    ShippingRateSerializer,
    ShippingMethodSerializer,
    ShippingMethodListSerializer,
    ShippingMethodCreateSerializer,
    ShippingMethodUpdateSerializer,
    ShippingRateCreateSerializer,
    ShippingCalculatorSerializer,
    ShippingCostResultSerializer,
)

# Inventory serializers
from .inventory_serializers import (
    SupplierSerializer,
    SupplierListSerializer,
    InventoryLocationSerializer,
    InventoryLocationListSerializer,
    StockMovementSerializer,
    StockMovementListSerializer,
    PurchaseOrderSerializer,
    PurchaseOrderListSerializer,
    InventorySerializer,
    InventoryListSerializer,
    InventoryUpdateSerializer,
    StockAdjustmentSerializer,
    InventoryTransferSerializer,
    InventoryStatsSerializer,
)

# Discounts serializers
from .discounts_serializers import (
    PriceRuleSerializer,
    PriceRuleListSerializer,
    CouponSerializer,
    CouponListSerializer,
    CouponCreateSerializer,
    CouponUpdateSerializer,
    CouponUsageSerializer,
    CouponUsageListSerializer,
    DiscountSerializer,
    DiscountListSerializer,
    CouponValidateSerializer,
    CouponValidationResultSerializer,
    DiscountCalculatorSerializer,
    DiscountStatsSerializer,
)

# Reviews serializers
from .reviews_serializers import (
    ReviewImageSerializer,
    ReviewHelpfulnessSerializer,
    ReviewSerializer,
    ReviewListSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    ReviewHelpfulnessCreateSerializer,
    ReviewModerationSerializer,
    ReviewStatsSerializer,
)

# Support serializers
from .support_serializers import (
    TicketCategorySerializer,
    FAQCategorySerializer,
    FAQSerializer,
    FAQListSerializer,
    TicketMessageSerializer,
    TicketMessageCreateSerializer,
    TicketSerializer,
    TicketListSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
    TicketStatusUpdateSerializer,
    SupportStatsSerializer,
)

# Blog serializers
from .blog_serializers import (
    BlogCategorySerializer,
    BlogCategoryListSerializer,
    BlogTagSerializer,
    BlogPostSerializer,
    BlogPostListSerializer,
    BlogPostCreateSerializer,
    BlogPostUpdateSerializer,
    BlogCommentSerializer,
    BlogCommentListSerializer,
    BlogCommentCreateSerializer,
    BlogStatsSerializer,
)

# Ads serializers
from .ads_serializers import (
    AdSpaceSerializer,
    AdSpaceListSerializer,
    AdBannerSerializer,
    AdBannerListSerializer,
    AdBannerCreateSerializer,
    AdBannerUpdateSerializer,
    AdImpressionSerializer,
    AdClickSerializer,
    AdStatsSerializer,
)

__all__ = [
    # Core
    'CountrySerializer', 'CountryListSerializer', 'CurrencySerializer',
    'SiteSettingsSerializer', 'ThemeConfigSerializer', 'ContactSerializer',
    'ContactListSerializer', 'AdminNoteSerializer', 'AdminNoteListSerializer',
    'SystemLogSerializer', 'SystemLogListSerializer', 'SiteStatsSerializer',
    'ThemeSerializer',
    
    # Accounts
    'UserPublicSerializer', 'UserProfileSerializer', 'UserAddressSerializer',
    'UserAddressListSerializer', 'UserSerializer', 'UserCreateSerializer',
    'UserUpdateSerializer', 'UserPasswordUpdateSerializer', 'UserPasswordResetSerializer',
    'UserPasswordResetConfirmSerializer', 'CustomTokenObtainPairSerializer',
    'LoginSerializer', 'SocialLoginSerializer', 'WishlistSerializer',
    'WishlistListSerializer', 'WishlistCreateSerializer', 'WishlistRemoveSerializer',
    'UserStatsSerializer',
    
    # Products
    'CategorySerializer', 'CategoryListSerializer', 'CategoryTreeSerializer',
    'BrandSerializer', 'BrandListSerializer', 'TagSerializer',
    'AttributeSerializer', 'AttributeListSerializer', 'AttributeValueSerializer',
    'AttributeValueListSerializer', 'ProductImageSerializer', 'ProductVariantSerializer',
    'ProductVariantListSerializer', 'ProductReviewSerializer', 'ProductSerializer',
    'ProductListSerializer', 'ProductCreateSerializer', 'ProductUpdateSerializer',
    'ProductVariantCreateSerializer', 'ProductVariantUpdateSerializer',
    'ProductSearchSerializer', 'ProductFilterSerializer', 'ProductStatsSerializer',
    
    # Cart
    'CartItemSerializer', 'CartItemListSerializer', 'CartItemCreateSerializer',
    'CartItemUpdateSerializer', 'CartSerializer', 'CartListSerializer',
    'AddToCartSerializer', 'UpdateCartItemSerializer', 'RemoveFromCartSerializer',
    'ClearCartSerializer', 'ApplyCouponSerializer', 'RemoveCouponSerializer',
    'CartSummarySerializer',
    
    # Orders
    'OrderItemSerializer', 'OrderItemListSerializer', 'ShippingSerializer',
    'ShippingListSerializer', 'OrderSerializer', 'OrderListSerializer',
    'OrderCreateSerializer', 'OrderUpdateSerializer', 'OrderStatusUpdateSerializer',
    'OrderCancelSerializer', 'OrderRefundSerializer', 'OrderStatsSerializer',
    'OrderExportSerializer',
    
    # Payments
    'PaymentMethodSerializer', 'PaymentMethodListSerializer', 'WalletSerializer',
    'WalletTransactionSerializer', 'WalletTransactionListSerializer', 'RefundSerializer',
    'RefundListSerializer', 'PaymentTransactionSerializer',
    'PaymentTransactionListSerializer', 'PaymentTransactionCreateSerializer',
    'PaymentVerifySerializer', 'PaymentCallbackSerializer', 'PaymentStatsSerializer',
    'PaymentGatewayConfigSerializer',
    
    # Shipping
    'ShippingZoneSerializer', 'ShippingClassSerializer', 'PickupLocationSerializer',
    'DeliveryTimeSerializer', 'ShippingRateSerializer', 'ShippingMethodSerializer',
    'ShippingMethodListSerializer', 'ShippingMethodCreateSerializer',
    'ShippingMethodUpdateSerializer', 'ShippingRateCreateSerializer',
    'ShippingCalculatorSerializer', 'ShippingCostResultSerializer',
    
    # Inventory
    'SupplierSerializer', 'SupplierListSerializer', 'InventoryLocationSerializer',
    'InventoryLocationListSerializer', 'StockMovementSerializer',
    'StockMovementListSerializer', 'PurchaseOrderSerializer',
    'PurchaseOrderListSerializer', 'InventorySerializer', 'InventoryListSerializer',
    'InventoryUpdateSerializer', 'StockAdjustmentSerializer',
    'InventoryTransferSerializer', 'InventoryStatsSerializer',
    
    # Discounts
    'PriceRuleSerializer', 'PriceRuleListSerializer', 'CouponSerializer',
    'CouponListSerializer', 'CouponCreateSerializer', 'CouponUpdateSerializer',
    'CouponUsageSerializer', 'CouponUsageListSerializer', 'DiscountSerializer',
    'DiscountListSerializer', 'CouponValidateSerializer',
    'CouponValidationResultSerializer', 'DiscountCalculatorSerializer',
    'DiscountStatsSerializer',
    
    # Reviews
    'ReviewImageSerializer', 'ReviewHelpfulnessSerializer', 'ReviewSerializer',
    'ReviewListSerializer', 'ReviewCreateSerializer', 'ReviewUpdateSerializer',
    'ReviewHelpfulnessCreateSerializer', 'ReviewModerationSerializer',
    'ReviewStatsSerializer',
    
    # Support
    'TicketCategorySerializer', 'FAQCategorySerializer', 'FAQSerializer',
    'FAQListSerializer', 'TicketMessageSerializer', 'TicketMessageCreateSerializer',
    'TicketSerializer', 'TicketListSerializer', 'TicketCreateSerializer',
    'TicketUpdateSerializer', 'TicketStatusUpdateSerializer', 'SupportStatsSerializer',
    
    # Blog
    'BlogCategorySerializer', 'BlogCategoryListSerializer', 'BlogTagSerializer',
    'BlogPostSerializer', 'BlogPostListSerializer', 'BlogPostCreateSerializer',
    'BlogPostUpdateSerializer', 'BlogCommentSerializer', 'BlogCommentListSerializer',
    'BlogCommentCreateSerializer', 'BlogStatsSerializer',
    
    # Ads
    'AdSpaceSerializer', 'AdSpaceListSerializer', 'AdBannerSerializer',
    'AdBannerListSerializer', 'AdBannerCreateSerializer', 'AdBannerUpdateSerializer',
    'AdImpressionSerializer', 'AdClickSerializer', 'AdStatsSerializer',
]
