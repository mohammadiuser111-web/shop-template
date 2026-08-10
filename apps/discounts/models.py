"""
Discount models for shop-template project.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Discount(models.Model):
    """
    Base model for discounts.
    """
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=50, unique=True, verbose_name='Code', blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, verbose_name='Discount Type')
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Discount Value')
    
    # Validity
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    start_date = models.DateTimeField(verbose_name='Start Date', null=True, blank=True)
    end_date = models.DateTimeField(verbose_name='End Date', null=True, blank=True)
    
    # Usage limits
    max_uses = models.PositiveIntegerField(verbose_name='Max Uses', null=True, blank=True)
    uses_count = models.PositiveIntegerField(default=0, verbose_name='Uses Count')
    max_uses_per_user = models.PositiveIntegerField(verbose_name='Max Uses Per User', null=True, blank=True)
    
    # Description
    description = models.TextField(verbose_name='Description', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def is_valid(self):
        """Check if discount is valid."""
        from django.utils import timezone
        
        now = timezone.now()
        
        # Check if active
        if not self.is_active:
            return False
        
        # Check date range
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        # Check max uses
        if self.max_uses and self.uses_count >= self.max_uses:
            return False
        
        return True
    
    def calculate_discount(self, amount):
        """Calculate discount amount."""
        if self.discount_type == 'percentage':
            return amount * (self.discount_value / 100)
        else:
            return self.discount_value


class Coupon(Discount):
    """
    Model for discount coupons.
    """
    COUPON_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('email', 'Email Restricted'),
        ('user', 'User Restricted'),
        ('product', 'Product Restricted'),
        ('category', 'Category Restricted'),
    ]
    
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPES, default='public',
                                    verbose_name='Coupon Type')
    
    # Restrictions
    min_order_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Minimum Order Amount',
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    max_order_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Maximum Order Amount',
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Product restrictions
    products = models.ManyToManyField(
        'products.Product',
        related_name='coupons',
        verbose_name='Products',
        blank=True
    )
    categories = models.ManyToManyField(
        'products.Category',
        related_name='coupons',
        verbose_name='Categories',
        blank=True
    )
    exclude_products = models.ManyToManyField(
        'products.Product',
        related_name='excluded_coupons',
        verbose_name='Exclude Products',
        blank=True
    )
    exclude_categories = models.ManyToManyField(
        'products.Category',
        related_name='excluded_coupons',
        verbose_name='Exclude Categories',
        blank=True
    )
    
    # User restrictions
    allowed_users = models.ManyToManyField(
        'accounts.User',
        related_name='allowed_coupons',
        verbose_name='Allowed Users',
        blank=True
    )
    allowed_emails = models.TextField(
        verbose_name='Allowed Emails',
        blank=True,
        help_text='Comma-separated list of email addresses'
    )
    
    # Free shipping
    free_shipping = models.BooleanField(default=False, verbose_name='Free Shipping')
    
    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def is_valid_for_order(self, order):
        """Check if coupon is valid for a specific order."""
        if not self.is_valid():
            return False
        
        # Check order amount
        if self.min_order_amount and order.total < self.min_order_amount:
            return False
        if self.max_order_amount and order.total > self.max_order_amount:
            return False
        
        # Check user restrictions
        if self.coupon_type == 'user' and order.user not in self.allowed_users.all():
            return False
        
        if self.coupon_type == 'email':
            allowed_emails = [e.strip() for e in self.allowed_emails.split(',') if e.strip()]
            if order.email not in allowed_emails:
                return False
        
        # Check product restrictions
        if self.products.exists():
            # At least one product in order must be in allowed products
            order_product_ids = set(order.items.values_list('product_id', flat=True))
            allowed_product_ids = set(self.products.values_list('id', flat=True))
            if not order_product_ids & allowed_product_ids:
                return False
        
        if self.categories.exists():
            # At least one product in order must be in allowed categories
            order_product_category_ids = set(
                order.items.values_list('product__category_id', flat=True)
            )
            allowed_category_ids = set(self.categories.values_list('id', flat=True))
            if not order_product_category_ids & allowed_category_ids:
                return False
        
        # Check excluded products
        if self.exclude_products.exists():
            order_product_ids = set(order.items.values_list('product_id', flat=True))
            excluded_product_ids = set(self.exclude_products.values_list('id', flat=True))
            if order_product_ids & excluded_product_ids:
                return False
        
        # Check excluded categories
        if self.exclude_categories.exists():
            order_product_category_ids = set(
                order.items.values_list('product__category_id', flat=True)
            )
            excluded_category_ids = set(self.exclude_categories.values_list('id', flat=True))
            if order_product_category_ids & excluded_category_ids:
                return False
        
        # Check user usage limit
        if self.max_uses_per_user:
            from apps.orders.models import Order
            user_uses = Order.objects.filter(
                user=order.user,
                coupon=self,
                payment_status='paid'
            ).count()
            if user_uses >= self.max_uses_per_user:
                return False
        
        return True
    
    def get_usage_count(self):
        """Get total usage count."""
        from apps.orders.models import Order
        return Order.objects.filter(coupon=self, payment_status='paid').count()
    
    def get_user_usage_count(self, user):
        """Get usage count for a specific user."""
        from apps.orders.models import Order
        return Order.objects.filter(
            user=user,
            coupon=self,
            payment_status='paid'
        ).count()


class Campaign(Discount):
    """
    Model for discount campaigns (automatic discounts).
    """
    CAMPAIGN_TYPES = [
        ('all_products', 'All Products'),
        ('specific_products', 'Specific Products'),
        ('specific_categories', 'Specific Categories'),
        ('bogo', 'Buy X Get Y'),
        ('tiered', 'Tiered Discount'),
    ]
    
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES, default='all_products',
                                     verbose_name='Campaign Type')
    
    # Products/Categories for specific campaigns
    products = models.ManyToManyField(
        'products.Product',
        related_name='campaigns',
        verbose_name='Products',
        blank=True
    )
    categories = models.ManyToManyField(
        'products.Category',
        related_name='campaigns',
        verbose_name='Categories',
        blank=True
    )
    
    # BOGO (Buy X Get Y) settings
    bogo_quantity = models.PositiveIntegerField(verbose_name='BOGO Quantity', null=True, blank=True)
    bogo_discount_type = models.CharField(
        max_length=20, 
        choices=DISCOUNT_TYPES, 
        verbose_name='BOGO Discount Type',
        null=True, 
        blank=True
    )
    bogo_discount_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='BOGO Discount Value',
        null=True, 
        blank=True
    )
    
    # Tiered discount settings
    tiers = models.JSONField(
        verbose_name='Tiered Discount Tiers',
        default=list,
        blank=True,
        help_text='JSON array of {min_quantity, discount_type, discount_value}'
    )
    
    # Priority (higher priority campaigns are applied first)
    priority = models.PositiveIntegerField(default=0, verbose_name='Priority')
    
    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_campaign_type_display()})"
    
    def is_applicable_to_product(self, product):
        """Check if campaign is applicable to a specific product."""
        if not self.is_valid():
            return False
        
        if self.campaign_type == 'all_products':
            return True
        elif self.campaign_type == 'specific_products':
            return product in self.products.all()
        elif self.campaign_type == 'specific_categories':
            return product.category in self.categories.all()
        
        return False
    
    def calculate_product_discount(self, product, quantity=1):
        """Calculate discount for a product."""
        if not self.is_applicable_to_product(product):
            return 0
        
        if self.campaign_type == 'bogo':
            # Buy X Get Y discount
            if quantity >= self.bogo_quantity:
                discount_qty = quantity // self.bogo_quantity
                if self.bogo_discount_type == 'percentage':
                    return product.get_price() * (self.bogo_discount_value / 100) * discount_qty
                else:
                    return self.bogo_discount_value * discount_qty
        elif self.campaign_type == 'tiered':
            # Tiered discount
            for tier in self.tiers:
                if quantity >= tier.get('min_quantity', 0):
                    if tier.get('discount_type') == 'percentage':
                        return product.get_price() * (tier.get('discount_value', 0) / 100) * quantity
                    else:
                        return tier.get('discount_value', 0) * quantity
        else:
            # Standard discount
            return super().calculate_discount(product.get_price() * quantity)
        
        return 0


class CouponUsage(models.Model):
    """
    Model for tracking coupon usage.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name='Coupon'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name='Order'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='coupon_usages',
        null=True,
        blank=True,
        verbose_name='User'
    )
    
    discount_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Discount Amount',
        default=0
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'
        ordering = ['-created_at']
        unique_together = [['coupon', 'order']]
    
    def __str__(self):
        return f"{self.coupon} - {self.order}"
