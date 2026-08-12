# ============================================
# Factories Package Initialization
# ============================================

"""
Factory classes for Shop Template test data generation.

All factory classes are defined in factories.py and re-exported here.
"""

from ..factories import *

__all__ = [
    # User factories
    'UserFactory',
    'StaffUserFactory',
    'AdminUserFactory',
    
    # Core factories
    'SiteSettingFactory',
    'SocialLinkFactory',
    'ContactInfoFactory',
    'MenuFactory',
    'MenuItemFactory',
    'PageFactory',
    
    # User profile factories
    'UserProfileFactory',
    'AddressFactory',
    
    # Product factories
    'CategoryFactory',
    'BrandFactory',
    'TagFactory',
    'ProductAttributeFactory',
    'ProductAttributeValueFactory',
    'ProductFactory',
    'ProductImageFactory',
    'ProductVariantFactory',
    'ProductAttributeValueRelationFactory',
    
    # Blog factories
    'BlogCategoryFactory',
    'BlogTagFactory',
    'BlogPostFactory',
    'BlogPostImageFactory',
    'CommentFactory',
    
    # Order factories
    'ShippingMethodFactory',
    'PaymentMethodFactory',
    'OrderFactory',
    'OrderItemFactory',
    'ShippingAddressFactory',
    'BillingAddressFactory',
    'PaymentFactory',
    
    # Review factories
    'ReviewFactory',
    'RatingFactory',
    
    # Wishlist factories
    'WishlistFactory',
    'WishlistItemFactory',
    
    # Compare factories
    'CompareFactory',
    'CompareItemFactory',
    
    # Coupon factories
    'CouponFactory',
    'CouponUsageFactory',
    
    # Newsletter factories
    'NewsletterSubscriptionFactory',
    'NewsletterCampaignFactory',
    
    # Notification factories
    'NotificationFactory',
    
    # Advertising factories
    'AdvertisementPlacementFactory',
    'ImpressionFactory',
]
