"""
Order models for shop-template project.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid


class Order(models.Model):
    """
    Model for customer orders.
    """
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('online', 'Online Payment'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Wallet'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Order Number')
    
    # Customer information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name='User'
    )
    first_name = models.CharField(max_length=100, verbose_name='First Name')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    email = models.EmailField(verbose_name='Email')
    phone_number = models.CharField(max_length=20, verbose_name='Phone Number')
    
    # Shipping information
    shipping_address_line_1 = models.CharField(max_length=255, verbose_name='Shipping Address Line 1')
    shipping_address_line_2 = models.CharField(max_length=255, verbose_name='Shipping Address Line 2', blank=True)
    shipping_city = models.CharField(max_length=100, verbose_name='Shipping City')
    shipping_state = models.CharField(max_length=100, verbose_name='Shipping State')
    shipping_postal_code = models.CharField(max_length=20, verbose_name='Shipping Postal Code')
    shipping_country = models.CharField(max_length=100, verbose_name='Shipping Country', default='Iran')
    
    # Billing information
    billing_address_line_1 = models.CharField(max_length=255, verbose_name='Billing Address Line 1')
    billing_address_line_2 = models.CharField(max_length=255, verbose_name='Billing Address Line 2', blank=True)
    billing_city = models.CharField(max_length=100, verbose_name='Billing City')
    billing_state = models.CharField(max_length=100, verbose_name='Billing State')
    billing_postal_code = models.CharField(max_length=20, verbose_name='Billing Postal Code')
    billing_country = models.CharField(max_length=100, verbose_name='Billing Country', default='Iran')
    
    # Order details
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Subtotal',
                                    validators=[MinValueValidator(0)])
    discount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Discount', default=0,
                                    validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Shipping Cost', default=0,
                                         validators=[MinValueValidator(0)])
    tax = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Tax', default=0,
                              validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total',
                                 validators=[MinValueValidator(0)])
    
    # Coupon
    coupon = models.ForeignKey(
        'discounts.Coupon',
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name='Coupon'
    )
    coupon_discount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Coupon Discount',
                                           default=0, validators=[MinValueValidator(0)])
    
    # Payment information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name='Payment Method')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending',
                                       verbose_name='Payment Status')
    payment_reference = models.CharField(max_length=200, verbose_name='Payment Reference', blank=True)
    payment_date = models.DateTimeField(verbose_name='Payment Date', null=True, blank=True)
    
    # Shipping information
    shipping_method = models.ForeignKey(
        'shipping.ShippingMethod',
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name='Shipping Method'
    )
    tracking_number = models.CharField(max_length=100, verbose_name='Tracking Number', blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', verbose_name='Status')
    
    # Notes
    customer_notes = models.TextField(verbose_name='Customer Notes', blank=True)
    admin_notes = models.TextField(verbose_name='Admin Notes', blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    shipped_at = models.DateTimeField(verbose_name='Shipped At', null=True, blank=True)
    delivered_at = models.DateTimeField(verbose_name='Delivered At', null=True, blank=True)
    cancelled_at = models.DateTimeField(verbose_name='Cancelled At', null=True, blank=True)
    
    # IP and user agent
    ip_address = models.GenericIPAddressField(verbose_name='IP Address', null=True, blank=True)
    user_agent = models.TextField(verbose_name='User Agent', blank=True)
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('accounts:order_detail', kwargs={'order_number': self.order_number})
    
    def get_full_name(self):
        """Get customer full name."""
        return f"{self.first_name} {self.last_name}"
    
    def get_shipping_address(self):
        """Get formatted shipping address."""
        address = f"{self.shipping_address_line_1}"
        if self.shipping_address_line_2:
            address += f", {self.shipping_address_line_2}"
        address += f"\n{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}"
        address += f"\n{self.shipping_country}"
        return address
    
    def get_billing_address(self):
        """Get formatted billing address."""
        address = f"{self.billing_address_line_1}"
        if self.billing_address_line_2:
            address += f", {self.billing_address_line_2}"
        address += f"\n{self.billing_city}, {self.billing_state} {self.billing_postal_code}"
        address += f"\n{self.billing_country}"
        return address
    
    def get_item_count(self):
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items.all())
    
    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in ['pending', 'processing', 'confirmed']
    
    def can_be_refunded(self):
        """Check if order can be refunded."""
        return self.status in ['delivered', 'shipped'] and self.payment_status == 'paid'
    
    def mark_as_paid(self):
        """Mark order as paid."""
        self.payment_status = 'paid'
        self.payment_date = models.DateTimeField(auto_now_add=True)
        self.save()
    
    def mark_as_shipped(self, tracking_number=None):
        """Mark order as shipped."""
        self.status = 'shipped'
        self.shipped_at = models.DateTimeField(auto_now_add=True)
        if tracking_number:
            self.tracking_number = tracking_number
        self.save()
    
    def mark_as_delivered(self):
        """Mark order as delivered."""
        self.status = 'delivered'
        self.delivered_at = models.DateTimeField(auto_now_add=True)
        self.save()
    
    def mark_as_cancelled(self):
        """Mark order as cancelled."""
        self.status = 'cancelled'
        self.cancelled_at = models.DateTimeField(auto_now_add=True)
        self.save()


class OrderItem(models.Model):
    """
    Model for order items.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Order'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        related_name='order_items',
        null=True,
        verbose_name='Product'
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        related_name='order_items',
        null=True,
        blank=True,
        verbose_name='Variant'
    )
    product_name = models.CharField(max_length=300, verbose_name='Product Name')
    product_sku = models.CharField(max_length=100, verbose_name='Product SKU')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Price',
                                 validators=[MinValueValidator(0)])
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Subtotal',
                                    validators=[MinValueValidator(0)])
    
    # Product snapshot (to preserve product data at time of purchase)
    product_snapshot = models.JSONField(verbose_name='Product Snapshot', default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.order} - {self.product_name}"
    
    def get_subtotal(self):
        """Calculate subtotal for this item."""
        return self.price * self.quantity


class OrderStatusHistory(models.Model):
    """
    Model for tracking order status changes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Order'
    )
    status = models.CharField(max_length=20, verbose_name='Status')
    notes = models.TextField(verbose_name='Notes', blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='order_status_changes',
        null=True,
        blank=True,
        verbose_name='Changed By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order} - {self.status}"


class Refund(models.Model):
    """
    Model for order refunds.
    """
    REFUND_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    REFUND_REASONS = [
        ('defective', 'Defective Product'),
        ('wrong_item', 'Wrong Item Shipped'),
        ('not_as_described', 'Not As Described'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name='Order'
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.SET_NULL,
        related_name='refunds',
        null=True,
        blank=True,
        verbose_name='Order Item'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Amount',
                                  validators=[MinValueValidator(0)])
    reason = models.CharField(max_length=20, choices=REFUND_REASONS, verbose_name='Reason')
    reason_details = models.TextField(verbose_name='Reason Details', blank=True)
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='pending',
                              verbose_name='Status')
    
    # Processing information
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='processed_refunds',
        null=True,
        blank=True,
        verbose_name='Processed By'
    )
    processed_at = models.DateTimeField(verbose_name='Processed At', null=True, blank=True)
    processing_notes = models.TextField(verbose_name='Processing Notes', blank=True)
    
    # Payment information
    payment_method = models.CharField(max_length=20, verbose_name='Payment Method', blank=True)
    transaction_id = models.CharField(max_length=200, verbose_name='Transaction ID', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund #{self.id} - {self.order}"
    
    def approve(self, processed_by, notes=None):
        """Approve the refund."""
        self.status = 'approved'
        self.processed_by = processed_by
        self.processed_at = models.DateTimeField(auto_now_add=True)
        if notes:
            self.processing_notes = notes
        self.save()
    
    def reject(self, processed_by, notes=None):
        """Reject the refund."""
        self.status = 'rejected'
        self.processed_by = processed_by
        self.processed_at = models.DateTimeField(auto_now_add=True)
        if notes:
            self.processing_notes = notes
        self.save()
    
    def complete(self, transaction_id=None, payment_method=None):
        """Mark refund as completed."""
        self.status = 'completed'
        if transaction_id:
            self.transaction_id = transaction_id
        if payment_method:
            self.payment_method = payment_method
        self.save()
