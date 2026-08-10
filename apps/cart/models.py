"""
Cart models for shop-template project.
"""
from django.db import models
from django.conf import settings
import uuid


class Cart(models.Model):
    """
    Model for shopping cart.
    """
    CART_TYPES = [
        ('session', 'Session Cart'),
        ('user', 'User Cart'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True,
        verbose_name='User'
    )
    session_key = models.CharField(max_length=40, verbose_name='Session Key', blank=True)
    cart_type = models.CharField(max_length=10, choices=CART_TYPES, default='session', verbose_name='Cart Type')
    
    # Coupon
    coupon = models.ForeignKey(
        'discounts.Coupon',
        on_delete=models.SET_NULL,
        related_name='carts',
        null=True,
        blank=True,
        verbose_name='Coupon'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"Cart #{self.id} - {self.user}"
        return f"Cart #{self.id} - Session"
    
    def get_subtotal(self):
        """Calculate subtotal (sum of all items without discount)."""
        return sum(item.get_subtotal() for item in self.items.all())
    
    def get_discount_amount(self):
        """Calculate discount amount from coupon."""
        if self.coupon and self.coupon.is_valid():
            subtotal = self.get_subtotal()
            if self.coupon.discount_type == 'percentage':
                return subtotal * (self.coupon.discount_value / 100)
            else:  # fixed
                return self.coupon.discount_value
        return 0
    
    def get_total(self):
        """Calculate total after discount."""
        return self.get_subtotal() - self.get_discount_amount()
    
    def get_item_count(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    def get_unique_item_count(self):
        """Get number of unique items in cart."""
        return self.items.count()
    
    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()
        self.coupon = None
        self.save()


class CartItem(models.Model):
    """
    Model for cart items.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Cart'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Product'
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='cart_items',
        null=True,
        blank=True,
        verbose_name='Variant'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    
    # Custom price (for special cases)
    custom_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Custom Price',
        null=True,
        blank=True
    )
    
    # Custom data (for external products or special configurations)
    custom_data = models.JSONField(verbose_name='Custom Data', default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['created_at']
        unique_together = [['cart', 'product', 'variant']]
    
    def __str__(self):
        if self.variant:
            return f"{self.cart} - {self.product.name} ({self.variant.name})"
        return f"{self.cart} - {self.product.name}"
    
    def get_price(self):
        """Get price for this item."""
        if self.custom_price:
            return self.custom_price
        elif self.variant:
            return self.variant.get_price()
        else:
            return self.product.get_price()
    
    def get_subtotal(self):
        """Calculate subtotal for this item."""
        return self.get_price() * self.quantity
    
    def get_product_name(self):
        """Get display name for this item."""
        if self.variant:
            return f"{self.product.name} - {self.variant.name}"
        return self.product.name
