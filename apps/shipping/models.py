"""
Shipping models for shop-template project.
"""
from django.db import models
from django.core.validators import MinValueValidator
import uuid


class ShippingZone(models.Model):
    """
    Model for shipping zones.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    description = models.TextField(verbose_name='Description', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Shipping Zone'
        verbose_name_plural = 'Shipping Zones'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class ShippingZoneLocation(models.Model):
    """
    Model for shipping zone locations (countries, states, cities, postal codes).
    """
    LOCATION_TYPES = [
        ('country', 'Country'),
        ('state', 'State'),
        ('city', 'City'),
        ('postal_code', 'Postal Code'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name='Shipping Zone'
    )
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, verbose_name='Location Type')
    location_code = models.CharField(max_length=100, verbose_name='Location Code')
    location_name = models.CharField(max_length=200, verbose_name='Location Name')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Shipping Zone Location'
        verbose_name_plural = 'Shipping Zone Locations'
        unique_together = [['zone', 'location_type', 'location_code']]
    
    def __str__(self):
        return f"{self.zone.name} - {self.location_name}"


class ShippingMethod(models.Model):
    """
    Model for shipping methods.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    
    # Zone
    zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.CASCADE,
        related_name='shipping_methods',
        verbose_name='Shipping Zone'
    )
    
    # Pricing
    PRICING_TYPES = [
        ('fixed', 'Fixed Price'),
        ('percentage', 'Percentage of Order'),
        ('per_item', 'Per Item'),
        ('per_weight', 'Per Weight'),
    ]
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES, default='fixed',
                                    verbose_name='Pricing Type')
    base_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Base Price',
                                      validators=[MinValueValidator(0)])
    price_per_kg = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Price Per KG',
                                        null=True, blank=True, validators=[MinValueValidator(0)])
    price_per_item = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Price Per Item',
                                          null=True, blank=True, validators=[MinValueValidator(0)])
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Percentage',
                                      null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Minimum and maximum
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Minimum Order Amount',
                                            null=True, blank=True, validators=[MinValueValidator(0)])
    max_order_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Maximum Order Amount',
                                            null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Estimated delivery time
    estimated_delivery_min = models.PositiveIntegerField(verbose_name='Estimated Delivery Min (days)', default=1)
    estimated_delivery_max = models.PositiveIntegerField(verbose_name='Estimated Delivery Max (days)', default=7)
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    is_free = models.BooleanField(default=False, verbose_name='Is Free')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    # Logo
    logo = models.ImageField(upload_to='shipping_methods/', verbose_name='Logo', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Shipping Method'
        verbose_name_plural = 'Shipping Methods'
        ordering = ['zone__sort_order', 'sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def calculate_cost(self, order):
        """Calculate shipping cost for an order."""
        if self.is_free:
            return 0
        
        if self.min_order_amount and order.total < self.min_order_amount:
            return None  # Not applicable
        
        if self.max_order_amount and order.total > self.max_order_amount:
            return None  # Not applicable
        
        if self.pricing_type == 'fixed':
            return self.base_price
        elif self.pricing_type == 'percentage':
            return order.total * (self.percentage / 100)
        elif self.pricing_type == 'per_item':
            return self.price_per_item * order.get_item_count()
        elif self.pricing_type == 'per_weight':
            total_weight = sum(
                item.product.weight * item.quantity 
                for item in order.items.all() 
                if item.product.weight
            )
            return self.price_per_kg * total_weight
        
        return self.base_price
    
    def get_estimated_delivery(self):
        """Get estimated delivery time range."""
        if self.estimated_delivery_min == self.estimated_delivery_max:
            return f"{self.estimated_delivery_min} روز"
        return f"{self.estimated_delivery_min} تا {self.estimated_delivery_max} روز"


class ShippingClass(models.Model):
    """
    Model for shipping classes (for products that require special shipping).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Shipping Class'
        verbose_name_plural = 'Shipping Classes'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PickupLocation(models.Model):
    """
    Model for pickup locations (for local pickup shipping method).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    address = models.TextField(verbose_name='Address')
    city = models.CharField(max_length=100, verbose_name='City')
    state = models.CharField(max_length=100, verbose_name='State')
    postal_code = models.CharField(max_length=20, verbose_name='Postal Code')
    country = models.CharField(max_length=100, verbose_name='Country', default='Iran')
    phone = models.CharField(max_length=20, verbose_name='Phone')
    email = models.EmailField(verbose_name='Email', blank=True)
    
    # Working hours
    opening_hours = models.CharField(max_length=200, verbose_name='Opening Hours', blank=True)
    
    # Coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name='Latitude', null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name='Longitude', null=True, blank=True)
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Pickup Location'
        verbose_name_plural = 'Pickup Locations'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_full_address(self):
        """Get formatted address."""
        address = f"{self.address}"
        address += f"\n{self.city}, {self.state} {self.postal_code}"
        address += f"\n{self.country}"
        return address
