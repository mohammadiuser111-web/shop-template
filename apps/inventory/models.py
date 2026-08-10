"""
Inventory models for shop-template project.
"""
from django.db import models
from django.conf import settings
import uuid


class Warehouse(models.Model):
    """
    Model for warehouses.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=20, unique=True, verbose_name='Code')
    address = models.TextField(verbose_name='Address')
    city = models.CharField(max_length=100, verbose_name='City')
    state = models.CharField(max_length=100, verbose_name='State')
    postal_code = models.CharField(max_length=20, verbose_name='Postal Code')
    country = models.CharField(max_length=100, verbose_name='Country', default='Iran')
    phone = models.CharField(max_length=20, verbose_name='Phone')
    email = models.EmailField(verbose_name='Email', blank=True)
    
    # Manager
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='managed_warehouses',
        null=True,
        blank=True,
        verbose_name='Manager'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_full_address(self):
        """Get formatted address."""
        address = f"{self.address}"
        address += f"\n{self.city}, {self.state} {self.postal_code}"
        address += f"\n{self.country}"
        return address


class Inventory(models.Model):
    """
    Model for tracking inventory levels.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='inventory_records',
        verbose_name='Product'
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='inventory_records',
        null=True,
        blank=True,
        verbose_name='Variant'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='inventory_records',
        verbose_name='Warehouse'
    )
    
    # Quantity
    quantity = models.PositiveIntegerField(default=0, verbose_name='Quantity')
    reserved_quantity = models.PositiveIntegerField(default=0, verbose_name='Reserved Quantity')
    low_stock_threshold = models.PositiveIntegerField(default=5, verbose_name='Low Stock Threshold')
    
    # Location in warehouse
    location = models.CharField(max_length=100, verbose_name='Location', blank=True)
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventory Records'
        unique_together = [['product', 'variant', 'warehouse']]
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.variant:
            return f"{self.warehouse.name} - {self.product.name} ({self.variant.name})"
        return f"{self.warehouse.name} - {self.product.name}"
    
    def get_available_quantity(self):
        """Get available quantity (total - reserved)."""
        return self.quantity - self.reserved_quantity
    
    def is_low_stock(self):
        """Check if inventory is low."""
        return self.get_available_quantity() <= self.low_stock_threshold
    
    def is_out_of_stock(self):
        """Check if inventory is out of stock."""
        return self.get_available_quantity() <= 0


class InventoryMovement(models.Model):
    """
    Model for tracking inventory movements (in/out).
    """
    MOVEMENT_TYPES = [
        ('in', 'In'),
        ('out', 'Out'),
        ('adjustment', 'Adjustment'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('return', 'Return'),
        ('damage', 'Damage'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='Inventory'
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, verbose_name='Movement Type')
    quantity = models.IntegerField(verbose_name='Quantity')
    quantity_after = models.IntegerField(verbose_name='Quantity After')
    
    # Reference
    reference_type = models.CharField(max_length=50, verbose_name='Reference Type', blank=True)
    reference_id = models.PositiveIntegerField(verbose_name='Reference ID', null=True, blank=True)
    
    # User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='inventory_movements',
        null=True,
        blank=True,
        verbose_name='User'
    )
    
    # Notes
    notes = models.TextField(verbose_name='Notes', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Inventory Movement'
        verbose_name_plural = 'Inventory Movements'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.inventory} - {self.quantity}"


class StockAlert(models.Model):
    """
    Model for stock alert notifications.
    """
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('back_in_stock', 'Back in Stock'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stock_alerts',
        verbose_name='Product'
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='stock_alerts',
        null=True,
        blank=True,
        verbose_name='Variant'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stock_alerts',
        verbose_name='Warehouse'
    )
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name='Alert Type')
    
    # Threshold
    threshold = models.PositiveIntegerField(default=5, verbose_name='Threshold')
    current_quantity = models.PositiveIntegerField(default=0, verbose_name='Current Quantity')
    
    # Notification
    is_notified = models.BooleanField(default=False, verbose_name='Is Notified')
    notified_at = models.DateTimeField(verbose_name='Notified At', null=True, blank=True)
    notified_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='stock_alert_notifications',
        verbose_name='Notified To',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Stock Alert'
        verbose_name_plural = 'Stock Alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.variant:
            return f"{self.alert_type} - {self.product.name} ({self.variant.name}) - {self.warehouse.name}"
        return f"{self.alert_type} - {self.product.name} - {self.warehouse.name}"


class Supplier(models.Model):
    """
    Model for suppliers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=20, unique=True, verbose_name='Code')
    contact_person = models.CharField(max_length=200, verbose_name='Contact Person', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Phone')
    email = models.EmailField(verbose_name='Email', blank=True)
    address = models.TextField(verbose_name='Address', blank=True)
    city = models.CharField(max_length=100, verbose_name='City', blank=True)
    state = models.CharField(max_length=100, verbose_name='State', blank=True)
    postal_code = models.CharField(max_length=20, verbose_name='Postal Code', blank=True)
    country = models.CharField(max_length=100, verbose_name='Country', default='Iran')
    
    # Tax information
    tax_id = models.CharField(max_length=100, verbose_name='Tax ID', blank=True)
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    # Notes
    notes = models.TextField(verbose_name='Notes', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_full_address(self):
        """Get formatted address."""
        address = f"{self.address}" if self.address else ""
        if self.city:
            address += f"\n{self.city}"
        if self.state:
            address += f", {self.state}"
        if self.postal_code:
            address += f" {self.postal_code}"
        if self.country:
            address += f"\n{self.country}"
        return address


class PurchaseOrder(models.Model):
    """
    Model for purchase orders from suppliers.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('ordered', 'Ordered'),
        ('partially_received', 'Partially Received'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    po_number = models.CharField(max_length=20, unique=True, verbose_name='PO Number')
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='purchase_orders',
        verbose_name='Supplier'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='purchase_orders',
        verbose_name='Warehouse'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Status')
    
    # Dates
    order_date = models.DateField(verbose_name='Order Date', null=True, blank=True)
    expected_delivery_date = models.DateField(verbose_name='Expected Delivery Date', null=True, blank=True)
    received_date = models.DateField(verbose_name='Received Date', null=True, blank=True)
    
    # Financial
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Subtotal', default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Tax', default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Shipping Cost', default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total', default=0)
    
    # User
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_purchase_orders',
        null=True,
        blank=True,
        verbose_name='Created By'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='approved_purchase_orders',
        null=True,
        blank=True,
        verbose_name='Approved By'
    )
    
    # Notes
    notes = models.TextField(verbose_name='Notes', blank=True)
    internal_notes = models.TextField(verbose_name='Internal Notes', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PO #{self.po_number}"
    
    def calculate_totals(self):
        """Calculate totals from items."""
        from django.db.models import Sum, F
        
        subtotal = self.items.aggregate(
            subtotal=Sum(F('quantity') * F('unit_price'))
        )['subtotal'] or 0
        
        self.subtotal = subtotal
        self.tax = subtotal * 0.09  # Default 9% tax
        self.total = subtotal + self.tax + self.shipping_cost
        self.save()


class PurchaseOrderItem(models.Model):
    """
    Model for purchase order items.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Purchase Order'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='purchase_order_items',
        verbose_name='Product'
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='purchase_order_items',
        null=True,
        blank=True,
        verbose_name='Variant'
    )
    
    # Item details
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Unit Price')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Subtotal')
    
    # Received quantity
    received_quantity = models.PositiveIntegerField(default=0, verbose_name='Received Quantity')
    
    # Status
    status = models.CharField(max_length=20, verbose_name='Status', blank=True)
    
    # Notes
    notes = models.TextField(verbose_name='Notes', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Purchase Order Item'
        verbose_name_plural = 'Purchase Order Items'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.purchase_order} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        """Calculate subtotal before saving."""
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
