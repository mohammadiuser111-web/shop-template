"""
Product models for shop-template project.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import uuid


class Category(models.Model):
    """
    Model for product categories.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name='Parent Category'
    )
    image = models.ImageField(upload_to='categories/', verbose_name='Image', null=True, blank=True)
    icon = models.CharField(max_length=50, verbose_name='Icon', blank=True, 
                           help_text='Feather icon name (e.g., "shopping-bag", "smartphone")')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    # SEO fields
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', blank=True)
    meta_keywords = models.TextField(verbose_name='Meta Keywords', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['parent__sort_order', 'sort_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:category', kwargs={'slug': self.slug})
    
    def get_children(self):
        """Get all direct children of this category."""
        return self.children.filter(is_active=True)
    
    def get_all_descendants(self):
        """Get all descendants (children, grandchildren, etc.) of this category."""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def get_ancestors(self):
        """Get all ancestors (parent, grandparent, etc.) of this category."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors


class Brand(models.Model):
    """
    Model for product brands.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    logo = models.ImageField(upload_to='brands/', verbose_name='Logo', null=True, blank=True)
    website = models.URLField(verbose_name='Website', blank=True)
    country = models.CharField(max_length=100, verbose_name='Country', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    # SEO fields
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:brand', kwargs={'slug': self.slug})


class Attribute(models.Model):
    """
    Model for product attributes (e.g., Color, Size, Material).
    """
    ATTRIBUTE_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('select', 'Select'),
        ('multiselect', 'Multi-select'),
        ('color', 'Color'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Name')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug')
    attribute_type = models.CharField(max_length=20, choices=ATTRIBUTE_TYPES, default='text', verbose_name='Type')
    description = models.TextField(verbose_name='Description', blank=True)
    is_filterable = models.BooleanField(default=True, verbose_name='Is Filterable')
    is_required = models.BooleanField(default=False, verbose_name='Is Required')
    is_variant = models.BooleanField(default=False, verbose_name='Is Variant',
                                    help_text='If checked, this attribute will create product variants')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = _('Attribute')
        verbose_name_plural = _('Attributes')
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_filterable']),
            models.Index(fields=['is_variant']),
        ]
    
    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    """
    Model for attribute values (e.g., Red, Blue, Large, Small).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='Attribute'
    )
    value = models.CharField(max_length=200, verbose_name='Value')
    color_code = models.CharField(max_length=20, verbose_name='Color Code', blank=True,
                                  help_text='Hex color code (e.g., #FF0000) for color attributes')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = _('Attribute Value')
        verbose_name_plural = _('Attribute Values')
        ordering = ['attribute__sort_order', 'sort_order', 'value']
        unique_together = [['attribute', 'value']]
        indexes = [
            models.Index(fields=['attribute']),
            models.Index(fields=['value']),
        ]
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(models.Model):
    """
    Model for products.
    """
    PRODUCT_TYPES = [
        ('simple', 'Simple Product'),
        ('variable', 'Variable Product'),
        ('digital', 'Digital Product'),
        ('external', 'External Product'),
    ]
    
    STOCK_STATUS = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('backorder', 'Backorder'),
        ('preorder', 'Preorder'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU')
    name = models.CharField(max_length=300, verbose_name='Name')
    slug = models.SlugField(max_length=300, unique=True, verbose_name='Slug')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='simple', verbose_name='Product Type')
    
    # Category and Brand
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
        verbose_name='Category'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
        verbose_name='Brand'
    )
    
    # Description and content
    short_description = models.TextField(verbose_name='Short Description', blank=True)
    description = models.TextField(verbose_name='Description', blank=True)
    specifications = models.JSONField(verbose_name='Specifications', default=dict, blank=True)
    
    # Pricing
    regular_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Regular Price',
        validators=[MinValueValidator(0)]
    )
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Sale Price',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Cost Price',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Stock Quantity')
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS, default='in_stock', verbose_name='Stock Status')
    low_stock_threshold = models.PositiveIntegerField(default=5, verbose_name='Low Stock Threshold')
    allow_backorders = models.BooleanField(default=False, verbose_name='Allow Backorders')
    
    # Weight and dimensions
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Weight (kg)', null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Length (cm)', null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Width (cm)', null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Height (cm)', null=True, blank=True)
    
    # Media
    featured_image = models.ImageField(upload_to='products/', verbose_name='Featured Image', null=True, blank=True)
    
    # Status and visibility
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    is_featured = models.BooleanField(default=False, verbose_name='Is Featured')
    is_best_seller = models.BooleanField(default=False, verbose_name='Is Best Seller')
    is_new = models.BooleanField(default=False, verbose_name='Is New')
    is_on_sale = models.BooleanField(default=False, verbose_name='Is On Sale')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    published_at = models.DateTimeField(verbose_name='Published At', null=True, blank=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', blank=True)
    meta_keywords = models.TextField(verbose_name='Meta Keywords', blank=True)
    
    # Related products
    related_products = models.ManyToManyField('self', blank=True, verbose_name='Related Products')
    upsell_products = models.ManyToManyField('self', blank=True, verbose_name='Upsell Products')
    cross_sell_products = models.ManyToManyField('self', blank=True, verbose_name='Cross-sell Products')
    
    # Tags
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='Tags')
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['product_type']),
            models.Index(fields=['stock_status']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:product_detail', kwargs={'slug': self.slug})
    
    def get_price(self):
        """Get the current price (sale price if available, otherwise regular price)."""
        return self.sale_price if self.sale_price else self.regular_price
    
    def get_discount_percentage(self):
        """Calculate discount percentage if product is on sale."""
        if self.sale_price and self.regular_price > 0:
            discount = (self.regular_price - self.sale_price) / self.regular_price * 100
            return round(discount, 2)
        return 0
    
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock_status == 'in_stock' and self.stock_quantity > 0
    
    def get_rating(self):
        """Get average rating from reviews."""
        from django.db.models import Avg
        from apps.reviews.models import Review
        return Review.objects.filter(product=self, is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0
    
    def get_review_count(self):
        """Get total number of approved reviews."""
        from apps.reviews.models import Review
        return Review.objects.filter(product=self, is_approved=True).count()


class ProductImage(models.Model):
    """
    Model for product images.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Product'
    )
    image = models.ImageField(upload_to='products/', verbose_name='Image')
    alt_text = models.CharField(max_length=200, verbose_name='Alt Text', blank=True)
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    is_featured = models.BooleanField(default=False, verbose_name='Is Featured')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.sort_order}"


class ProductAttribute(models.Model):
    """
    Model for product attribute values.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_attributes',
        verbose_name='Product'
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='product_attributes',
        verbose_name='Attribute'
    )
    value = models.CharField(max_length=200, verbose_name='Value')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = _('Product Attribute')
        verbose_name_plural = _('Product Attributes')
        unique_together = [['product', 'attribute']]
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"


class ProductVariant(models.Model):
    """
    Model for product variants (e.g., different colors, sizes).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name='Product'
    )
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU')
    name = models.CharField(max_length=300, verbose_name='Variant Name')
    
    # Variant attribute values
    attribute_values = models.ManyToManyField(
        AttributeValue,
        related_name='variants',
        verbose_name='Attribute Values'
    )
    
    # Pricing (can override parent product)
    regular_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Regular Price',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Sale Price',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Stock Quantity')
    stock_status = models.CharField(max_length=20, choices=Product.STOCK_STATUS, 
                                     default='in_stock', verbose_name='Stock Status')
    
    # Weight and dimensions (can override parent product)
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Weight (kg)', 
                                  null=True, blank=True)
    
    # Media
    image = models.ImageField(upload_to='products/variants/', verbose_name='Image', null=True, blank=True)
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    def get_price(self):
        """Get the current price (sale price if available, otherwise regular price)."""
        if self.sale_price:
            return self.sale_price
        elif self.regular_price:
            return self.regular_price
        else:
            return self.product.get_price()
    
    def is_in_stock(self):
        """Check if variant is in stock."""
        return self.stock_status == 'in_stock' and self.stock_quantity > 0


class Tag(models.Model):
    """
    Model for product tags.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Name')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    color = models.CharField(max_length=20, verbose_name='Color', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:tag', kwargs={'slug': self.slug})


class ProductCategory(models.Model):
    """
    Through model for many-to-many relationship between Product and Category.
    Allows for additional fields on the relationship.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False, verbose_name='Is Featured')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    class Meta:
        unique_together = [['product', 'category']]
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'
    
    def __str__(self):
        return f"{self.product.name} - {self.category.name}"
