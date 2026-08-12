# ============================================
# Factory Boy Factories for Shop Template
# ============================================

import factory
import factory.fuzzy
from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model

# Initialize Faker
fake = Faker()

# ============================================
# User Model Factory
# ============================================

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for User model"""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True
    is_staff = False
    is_superuser = False
    date_joined = factory.LazyFunction(timezone.now)
    last_login = None


class StaffUserFactory(UserFactory):
    """Factory for Staff User"""
    is_staff = True


class AdminUserFactory(UserFactory):
    """Factory for Admin User"""
    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f'admin{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@admin.com')


# ============================================
# Core Model Factories
# ============================================


class SiteSettingFactory(factory.django.DjangoModelFactory):
    """Factory for SiteSetting model"""
    
    class Meta:
        model = 'core.SiteSetting'
    
    key = factory.Sequence(lambda n: f'setting_{n}')
    value = factory.Faker('text', max_nb_chars=100)
    description = factory.Faker('sentence')


class SocialLinkFactory(factory.django.DjangoModelFactory):
    """Factory for SocialLink model"""
    
    class Meta:
        model = 'core.SocialLink'
    
    platform = factory.Faker('random_element', elements=['facebook', 'twitter', 'instagram', 'linkedin', 'youtube'])
    url = factory.Faker('url')
    icon = factory.Faker('random_element', elements=['fa-facebook', 'fa-twitter', 'fa-instagram', 'fa-linkedin', 'fa-youtube'])
    is_active = True
    sort_order = factory.Sequence(lambda n: n)


class ContactInfoFactory(factory.django.DjangoModelFactory):
    """Factory for ContactInfo model"""
    
    class Meta:
        model = 'core.ContactInfo'
    
    type = factory.Faker('random_element', elements=['email', 'phone', 'address', 'whatsapp'])
    value = factory.Faker('text', max_nb_chars=50)
    icon = factory.Faker('random_element', elements=['fa-envelope', 'fa-phone', 'fa-map-marker', 'fa-whatsapp'])
    is_active = True
    sort_order = factory.Sequence(lambda n: n)


class MenuFactory(factory.django.DjangoModelFactory):
    """Factory for Menu model"""
    
    class Meta:
        model = 'core.Menu'
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: f'menu-{obj.name.lower()}')
    description = factory.Faker('sentence')
    is_active = True
    sort_order = factory.Sequence(lambda n: n)


class MenuItemFactory(factory.django.DjangoModelFactory):
    """Factory for MenuItem model"""
    
    class Meta:
        model = 'core.MenuItem'
    
    menu = factory.SubFactory(MenuFactory)
    title = factory.Faker('word')
    url = factory.Faker('uri')
    parent = None
    is_active = True
    sort_order = factory.Sequence(lambda n: n)
    target_blank = False
    icon = factory.Faker('random_element', elements=['fa-home', 'fa-shop', 'fa-blog', 'fa-contact'])


class PageFactory(factory.django.DjangoModelFactory):
    """Factory for Page model"""
    
    class Meta:
        model = 'core.Page'
    
    title = factory.Faker('sentence', nb_words=3)
    slug = factory.LazyAttribute(lambda obj: f'page-{obj.title.lower().replace(" ", "-")}')
    content = factory.Faker('text', max_nb_chars=1000)
    is_active = True
    is_published = True
    published_at = factory.LazyFunction(timezone.now)
    sort_order = factory.Sequence(lambda n: n)
    meta_title = factory.LazyAttribute(lambda obj: obj.title)
    meta_description = factory.Faker('sentence')
    meta_keywords = factory.Faker('words', nb=5)


class AdvertisementFactory(factory.django.DjangoModelFactory):
    """Factory for Advertisement model"""
    
    class Meta:
        model = 'core.Advertisement'
    
    placement = factory.SubFactory('core.AdvertisementPlacementFactory')
    title = factory.Faker('sentence', nb_words=3)
    content = factory.Faker('text', max_nb_chars=500)
    url = factory.Faker('url')
    image = None
    is_active = True
    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=30))
    impressions = factory.Faker('random_int', min=0, max=10000)
    clicks = factory.Faker('random_int', min=0, max=1000)
    sort_order = factory.Sequence(lambda n: n)


class AdvertisementPlacementFactory(factory.django.DjangoModelFactory):
    """Factory for AdvertisementPlacement model"""
    
    class Meta:
        model = 'core.AdvertisementPlacement'
    
    name = factory.Sequence(lambda n: f'placement_{n}')
    description = factory.Faker('sentence')
    is_active = True


# ============================================
# User Profile Factories
# ============================================


class UserProfileFactory(factory.django.DjangoModelFactory):
    """Factory for UserProfile model"""
    
    class Meta:
        model = 'users.UserProfile'
    
    user = factory.SubFactory(UserFactory)
    phone = factory.Faker('phone_number')
    bio = factory.Faker('text', max_nb_chars=200)
    birth_date = factory.Faker('date_of_birth')
    gender = factory.Faker('random_element', elements=['male', 'female', 'other'])
    avatar = None
    newsletter_subscribed = True
    language = 'en'
    timezone = 'UTC'


class AddressFactory(factory.django.DjangoModelFactory):
    """Factory for Address model"""
    
    class Meta:
        model = 'users.Address'
    
    user = factory.SubFactory(UserFactory)
    address_type = factory.Faker('random_element', elements=['billing', 'shipping', 'both'])
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    company = factory.Faker('company')
    address_line_1 = factory.Faker('street_address')
    address_line_2 = factory.Faker('secondary_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    postal_code = factory.Faker('zipcode')
    country = factory.Faker('country_code')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    is_default = False
    notes = factory.Faker('sentence')


# ============================================
# Product Model Factories
# ============================================


class CategoryFactory(factory.django.DjangoModelFactory):
    """Factory for Category model"""
    
    class Meta:
        model = 'products.Category'
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: f'category-{obj.name.lower()}')
    description = factory.Faker('text', max_nb_chars=500)
    parent = None
    icon = factory.Faker('random_element', elements=['electronics', 'clothing', 'books', 'sports', 'home'])
    image = None
    is_featured = False
    is_active = True
    sort_order = factory.Sequence(lambda n: n)
    meta_title = factory.LazyAttribute(lambda obj: obj.name)
    meta_description = factory.Faker('sentence')
    meta_keywords = factory.Faker('words', nb=5)


class BrandFactory(factory.django.DjangoModelFactory):
    """Factory for Brand model"""
    
    class Meta:
        model = 'products.Brand'
    
    name = factory.Faker('company')
    slug = factory.LazyAttribute(lambda obj: f'brand-{obj.name.lower().replace(" ", "-")}')
    description = factory.Faker('text', max_nb_chars=500)
    logo = None
    website = factory.Faker('url')
    is_featured = False
    is_active = True
    sort_order = factory.Sequence(lambda n: n)
    meta_title = factory.LazyAttribute(lambda obj: obj.name)
    meta_description = factory.Faker('sentence')


class TagFactory(factory.django.DjangoModelFactory):
    """Factory for Tag model"""
    
    class Meta:
        model = 'products.Tag'
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())
    description = factory.Faker('sentence')


class ProductAttributeFactory(factory.django.DjangoModelFactory):
    """Factory for ProductAttribute model"""
    
    class Meta:
        model = 'products.ProductAttribute'
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: f'attr-{obj.name.lower()}')
    type = factory.Faker('random_element', elements=['text', 'number', 'color', 'size', 'boolean'])
    is_filterable = True
    is_variant = False
    is_active = True
    sort_order = factory.Sequence(lambda n: n)


class ProductAttributeValueFactory(factory.django.DjangoModelFactory):
    """Factory for ProductAttributeValue model"""
    
    class Meta:
        model = 'products.ProductAttributeValue'
    
    attribute = factory.SubFactory(ProductAttributeFactory)
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: f'value-{obj.name.lower()}')
    color_code = factory.Faker('hex_color')
    sort_order = factory.Sequence(lambda n: n)


class ProductFactory(factory.django.DjangoModelFactory):
    """Factory for Product model"""
    
    class Meta:
        model = 'products.Product'
    
    name = factory.Faker('sentence', nb_words=3)
    slug = factory.LazyAttribute(lambda obj: f'product-{obj.name.lower().replace(" ", "-")[:50]}')
    description = factory.Faker('text', max_nb_chars=2000)
    short_description = factory.Faker('text', max_nb_chars=200)
    sku = factory.Sequence(lambda n: f'SKU{n:08d}')
    category = factory.SubFactory(CategoryFactory)
    brand = factory.SubFactory(BrandFactory)
    regular_price = factory.Faker('random_int', min=10, max=1000)
    sale_price = factory.LazyAttribute(lambda obj: obj.regular_price * 0.8 if obj.regular_price > 50 else None)
    cost_price = factory.LazyAttribute(lambda obj: obj.regular_price * 0.7)
    weight = factory.Faker('random_int', min=100, max=5000)
    weight_unit = 'g'
    length = factory.Faker('random_int', min=1, max=100)
    width = factory.Faker('random_int', min=1, max=100)
    height = factory.Faker('random_int', min=1, max=100)
    dimension_unit = 'cm'
    stock_quantity = factory.Faker('random_int', min=0, max=1000)
    low_stock_threshold = 10
    is_in_stock = True
    is_featured = False
    is_popular = False
    is_new = False
    is_bestseller = False
    is_active = True
    is_digital = False
    is_shippable = True
    is_taxable = True
    tax_rate = 0.1
    sort_order = factory.Sequence(lambda n: n)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
    published_at = factory.LazyFunction(timezone.now)
    meta_title = factory.LazyAttribute(lambda obj: obj.name)
    meta_description = factory.Faker('sentence')
    meta_keywords = factory.Faker('words', nb=5)


class ProductImageFactory(factory.django.DjangoModelFactory):
    """Factory for ProductImage model"""
    
    class Meta:
        model = 'products.ProductImage'
    
    product = factory.SubFactory(ProductFactory)
    image = None
    alt_text = factory.Faker('sentence', nb_words=3)
    is_primary = False
    sort_order = factory.Sequence(lambda n: n)


class ProductVariantFactory(factory.django.DjangoModelFactory):
    """Factory for ProductVariant model"""
    
    class Meta:
        model = 'products.ProductVariant'
    
    product = factory.SubFactory(ProductFactory)
    sku = factory.LazyAttribute(lambda obj: f'{obj.product.sku}-VAR{obj.id}')
    name = factory.LazyAttribute(lambda obj: f'{obj.product.name} - Variant')
    regular_price = factory.LazyAttribute(lambda obj: obj.product.regular_price)
    sale_price = factory.LazyAttribute(lambda obj: obj.product.sale_price)
    cost_price = factory.LazyAttribute(lambda obj: obj.product.cost_price)
    weight = factory.LazyAttribute(lambda obj: obj.product.weight)
    stock_quantity = factory.Faker('random_int', min=0, max=100)
    is_default = False
    is_active = True
    sort_order = factory.Sequence(lambda n: n)


class ProductAttributeValueRelationFactory(factory.django.DjangoModelFactory):
    """Factory for ProductAttributeValueRelation model"""
    
    class Meta:
        model = 'products.ProductAttributeValueRelation'
    
    product = factory.SubFactory(ProductFactory)
    attribute = factory.SubFactory(ProductAttributeFactory)
    value = factory.SubFactory(ProductAttributeValueFactory)


# ============================================
# Blog Model Factories
# ============================================


class BlogCategoryFactory(factory.django.DjangoModelFactory):
    """Factory for BlogCategory model"""
    
    class Meta:
        model = 'blog.BlogCategory'
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: f'blog-category-{obj.name.lower()}')
    description = factory.Faker('text', max_nb_chars=500)
    parent = None
    is_featured = False
    is_active = True
    sort_order = factory.Sequence(lambda n: n)
    meta_title = factory.LazyAttribute(lambda obj: obj.name)
    meta_description = factory.Faker('sentence')


class BlogTagFactory(factory.django.DjangoModelFactory):
    """Factory for BlogTag model"""
    
    class Meta:
        model = 'blog.BlogTag'
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: f'blog-tag-{obj.name.lower()}')
    description = factory.Faker('sentence')


class BlogPostFactory(factory.django.DjangoModelFactory):
    """Factory for BlogPost model"""
    
    class Meta:
        model = 'blog.BlogPost'
    
    title = factory.Faker('sentence', nb_words=5)
    slug = factory.LazyAttribute(lambda obj: f'blog-post-{obj.title.lower().replace(" ", "-")[:100]}')
    excerpt = factory.Faker('text', max_nb_chars=200)
    content = factory.Faker('text', max_nb_chars=5000)
    category = factory.SubFactory(BlogCategoryFactory)
    author = factory.SubFactory(UserFactory)
    featured_image = None
    is_featured = False
    is_popular = False
    is_published = True
    published_at = factory.LazyFunction(timezone.now)
    is_comment_enabled = True
    comment_count = factory.Faker('random_int', min=0, max=50)
    view_count = factory.Faker('random_int', min=0, max=10000)
    like_count = factory.Faker('random_int', min=0, max=500)
    reading_time = factory.Faker('random_int', min=1, max=20)
    is_active = True
    sort_order = factory.Sequence(lambda n: n)
    meta_title = factory.LazyAttribute(lambda obj: obj.title)
    meta_description = factory.Faker('sentence')
    meta_keywords = factory.Faker('words', nb=5)


class BlogPostImageFactory(factory.django.DjangoModelFactory):
    """Factory for BlogPostImage model"""
    
    class Meta:
        model = 'blog.BlogPostImage'
    
    post = factory.SubFactory(BlogPostFactory)
    image = None
    alt_text = factory.Faker('sentence', nb_words=3)
    sort_order = factory.Sequence(lambda n: n)


class CommentFactory(factory.django.DjangoModelFactory):
    """Factory for Comment model"""
    
    class Meta:
        model = 'blog.Comment'
    
    post = factory.SubFactory(BlogPostFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Faker('text', max_nb_chars=500)
    is_approved = True
    is_spam = False
    parent = None
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


# ============================================
# Order Model Factories
# ============================================


class ShippingMethodFactory(factory.django.DjangoModelFactory):
    """Factory for ShippingMethod model"""
    
    class Meta:
        model = 'shipping.ShippingMethod'
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: f'shipping-{obj.name.lower()}')
    description = factory.Faker('sentence')
    cost = factory.Faker('random_int', min=0, max=50)
    is_active = True
    sort_order = factory.Sequence(lambda n: n)


class PaymentMethodFactory(factory.django.DjangoModelFactory):
    """Factory for PaymentMethod model"""
    
    class Meta:
        model = 'payments.PaymentMethod'
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: f'payment-{obj.name.lower()}')
    description = factory.Faker('sentence')
    is_active = True
    sort_order = factory.Sequence(lambda n: n)


class OrderFactory(factory.django.DjangoModelFactory):
    """Factory for Order model"""
    
    class Meta:
        model = 'orders.Order'
    
    user = factory.SubFactory(UserFactory)
    order_number = factory.Sequence(lambda n: f'ORD{n:08d}')
    status = factory.Faker('random_element', elements=['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'])
    payment_status = factory.Faker('random_element', elements=['pending', 'paid', 'failed', 'refunded'])
    shipping_status = factory.Faker('random_element', elements=['pending', 'shipped', 'delivered', 'returned'])
    shipping_method = factory.SubFactory(ShippingMethodFactory)
    payment_method = factory.SubFactory(PaymentMethodFactory)
    subtotal = factory.Faker('random_int', min=10, max=1000)
    tax = factory.LazyAttribute(lambda obj: obj.subtotal * 0.1)
    shipping_cost = factory.Faker('random_int', min=0, max=50)
    discount = factory.Faker('random_int', min=0, max=100)
    total = factory.LazyAttribute(lambda obj: obj.subtotal + obj.tax + obj.shipping_cost - obj.discount)
    currency = 'USD'
    notes = factory.Faker('sentence')
    is_guest = False
    ip_address = factory.Faker('ipv4')
    user_agent = factory.Faker('user_agent')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class OrderItemFactory(factory.django.DjangoModelFactory):
    """Factory for OrderItem model"""
    
    class Meta:
        model = 'orders.OrderItem'
    
    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    variant = factory.SubFactory(ProductVariantFactory)
    quantity = factory.Faker('random_int', min=1, max=10)
    price = factory.Faker('random_int', min=10, max=1000)
    total = factory.LazyAttribute(lambda obj: obj.price * obj.quantity)
    notes = factory.Faker('sentence')


class ShippingAddressFactory(factory.django.DjangoModelFactory):
    """Factory for ShippingAddress model"""
    
    class Meta:
        model = 'orders.ShippingAddress'
    
    order = factory.SubFactory(OrderFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    company = factory.Faker('company')
    address_line_1 = factory.Faker('street_address')
    address_line_2 = factory.Faker('secondary_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    postal_code = factory.Faker('zipcode')
    country = factory.Faker('country_code')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    notes = factory.Faker('sentence')


class BillingAddressFactory(factory.django.DjangoModelFactory):
    """Factory for BillingAddress model"""
    
    class Meta:
        model = 'orders.BillingAddress'
    
    order = factory.SubFactory(OrderFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    company = factory.Faker('company')
    address_line_1 = factory.Faker('street_address')
    address_line_2 = factory.Faker('secondary_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    postal_code = factory.Faker('zipcode')
    country = factory.Faker('country_code')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    tax_number = factory.Faker('random_number', digits=10)
    notes = factory.Faker('sentence')


class PaymentFactory(factory.django.DjangoModelFactory):
    """Factory for Payment model"""
    
    class Meta:
        model = 'payments.Payment'
    
    order = factory.SubFactory(OrderFactory)
    payment_method = factory.SubFactory(PaymentMethodFactory)
    transaction_id = factory.Sequence(lambda n: f'TRX{n:012d}')
    amount = factory.Faker('random_int', min=10, max=1000)
    currency = 'USD'
    status = factory.Faker('random_element', elements=['pending', 'completed', 'failed', 'refunded'])
    payment_data = factory.LazyAttribute(lambda obj: {'transaction_id': obj.transaction_id})
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


# ============================================
# Review Model Factories
# ============================================


class ReviewFactory(factory.django.DjangoModelFactory):
    """Factory for Review model"""
    
    class Meta:
        model = 'reviews.Review'
    
    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=3)
    content = factory.Faker('text', max_nb_chars=500)
    rating = factory.Faker('random_int', min=1, max=5)
    is_approved = True
    is_spam = False
    helpful_count = factory.Faker('random_int', min=0, max=50)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class RatingFactory(factory.django.DjangoModelFactory):
    """Factory for Rating model"""
    
    class Meta:
        model = 'reviews.Rating'
    
    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)
    value = factory.Faker('random_int', min=1, max=5)
    created_at = factory.LazyFunction(timezone.now)


# ============================================
# Wishlist Model Factories
# ============================================


class WishlistFactory(factory.django.DjangoModelFactory):
    """Factory for Wishlist model"""
    
    class Meta:
        model = 'wishlist.Wishlist'
    
    user = factory.SubFactory(UserFactory)
    is_active = True
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class WishlistItemFactory(factory.django.DjangoModelFactory):
    """Factory for WishlistItem model"""
    
    class Meta:
        model = 'wishlist.WishlistItem'
    
    wishlist = factory.SubFactory(WishlistFactory)
    product = factory.SubFactory(ProductFactory)
    variant = factory.SubFactory(ProductVariantFactory)
    quantity = 1
    notes = factory.Faker('sentence')
    created_at = factory.LazyFunction(timezone.now)


# ============================================
# Compare Model Factories
# ============================================


class CompareFactory(factory.django.DjangoModelFactory):
    """Factory for Compare model"""
    
    class Meta:
        model = 'compare.Compare'
    
    user = factory.SubFactory(UserFactory)
    is_active = True
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class CompareItemFactory(factory.django.DjangoModelFactory):
    """Factory for CompareItem model"""
    
    class Meta:
        model = 'compare.CompareItem'
    
    compare = factory.SubFactory(CompareFactory)
    product = factory.SubFactory(ProductFactory)
    variant = factory.SubFactory(ProductVariantFactory)
    created_at = factory.LazyFunction(timezone.now)


# ============================================
# Coupon Model Factories
# ============================================


class CouponFactory(factory.django.DjangoModelFactory):
    """Factory for Coupon model"""
    
    class Meta:
        model = 'coupons.Coupon'
    
    code = factory.Sequence(lambda n: f'COUPON{n:08d}')
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=200)
    discount_type = factory.Faker('random_element', elements=['percentage', 'fixed', 'free_shipping'])
    discount_value = factory.Faker('random_int', min=5, max=50)
    min_order_amount = factory.Faker('random_int', min=0, max=100)
    max_order_amount = factory.Faker('random_int', min=100, max=1000)
    usage_limit = factory.Faker('random_int', min=1, max=100)
    per_user_limit = factory.Faker('random_int', min=1, max=5)
    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=30))
    is_active = True
    applies_to = factory.Faker('random_element', elements=['all', 'specific_categories', 'specific_products', 'specific_users'])


class CouponUsageFactory(factory.django.DjangoModelFactory):
    """Factory for CouponUsage model"""
    
    class Meta:
        model = 'coupons.CouponUsage'
    
    coupon = factory.SubFactory(CouponFactory)
    user = factory.SubFactory(UserFactory)
    order = factory.SubFactory(OrderFactory)
    created_at = factory.LazyFunction(timezone.now)


# ============================================
# Newsletter Model Factories
# ============================================


class NewsletterSubscriptionFactory(factory.django.DjangoModelFactory):
    """Factory for NewsletterSubscription model"""
    
    class Meta:
        model = 'newsletter.NewsletterSubscription'
    
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_verified = True
    verify_token = factory.LazyAttribute(lambda obj: f'token-{obj.email}')
    subscribed_at = factory.LazyFunction(timezone.now)
    unsubscribed_at = None


class NewsletterCampaignFactory(factory.django.DjangoModelFactory):
    """Factory for NewsletterCampaign model"""
    
    class Meta:
        model = 'newsletter.NewsletterCampaign'
    
    title = factory.Faker('sentence', nb_words=3)
    subject = factory.Faker('sentence', nb_words=5)
    content = factory.Faker('text', max_nb_chars=5000)
    sender_email = factory.Faker('email')
    sender_name = factory.Faker('name')
    status = factory.Faker('random_element', elements=['draft', 'scheduled', 'sending', 'sent', 'cancelled'])
    scheduled_at = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=1))
    sent_at = None
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


# ============================================
# Notification Model Factories
# ============================================


class NotificationFactory(factory.django.DjangoModelFactory):
    """Factory for Notification model"""
    
    class Meta:
        model = 'notifications.Notification'
    
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=3)
    message = factory.Faker('text', max_nb_chars=500)
    type = factory.Faker('random_element', elements=['info', 'warning', 'error', 'success'])
    is_read = False
    url = factory.Faker('uri')
    data = factory.LazyAttribute(lambda obj: {'notification_id': obj.id})
    created_at = factory.LazyFunction(timezone.now)


# ============================================
# Advertising Model Factories
# ============================================


class AdvertisementFactory(factory.django.DjangoModelFactory):
    """Factory for Advertisement model"""
    
    class Meta:
        model = 'advertising.Advertisement'
    
    placement = factory.SubFactory('advertising.AdvertisementPlacementFactory')
    title = factory.Faker('sentence', nb_words=3)
    content = factory.Faker('text', max_nb_chars=500)
    url = factory.Faker('url')
    image = None
    is_active = True
    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=30))
    impressions = factory.Faker('random_int', min=0, max=10000)
    clicks = factory.Faker('random_int', min=0, max=1000)
    sort_order = factory.Sequence(lambda n: n)


class AdvertisementPlacementFactory(factory.django.DjangoModelFactory):
    """Factory for AdvertisementPlacement model"""
    
    class Meta:
        model = 'advertising.AdvertisementPlacement'
    
    name = factory.Sequence(lambda n: f'placement_{n}')
    description = factory.Faker('sentence')
    is_active = True


class ImpressionFactory(factory.django.DjangoModelFactory):
    """Factory for Impression model"""
    
    class Meta:
        model = 'advertising.Impression'
    
    advertisement = factory.SubFactory(AdvertisementFactory)
    user = factory.SubFactory(UserFactory)
    ip_address = factory.Faker('ipv4')
    user_agent = factory.Faker('user_agent')
    referrer = factory.Faker('uri')
    created_at = factory.LazyFunction(timezone.now)


# ============================================
# Export All Factories
# ============================================

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
    'AdvertisementFactory',
    'AdvertisementPlacementFactory',
    
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
    'AdvertisementFactory',
    'AdvertisementPlacementFactory',
    'ImpressionFactory',
]
