"""
Unit tests for Product application models.
Tests Category, Brand, Tag, Product, ProductImage, ProductVariant, Attribute, AttributeValue models.
"""

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


class TestCategory:
    """Tests for Category model"""
    
    def test_category_creation(self, db):
        """Test creating a category"""
        from apps.products.models import Category
        category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronics category',
            is_active=True,
            sort_order=0
        )
        
        assert category.name == 'Electronics'
        assert category.slug == 'electronics'
        assert category.description == 'Electronics category'
        assert category.is_active is True
        assert str(category) == 'Electronics'
    
    def test_category_str(self, db):
        """Test string representation of category"""
        from apps.products.models import Category
        category = Category.objects.create(name='Books', slug='books')
        assert str(category) == 'Books'
    
    def test_category_slug_generation(self, db):
        """Test category slug generation"""
        from apps.products.models import Category
        category = Category.objects.create(name='Web Development', slug='web-development')
        assert category.slug == 'web-development'
    
    def test_category_parent_relationship(self, db):
        """Test category parent relationship"""
        from apps.products.models import Category
        parent = Category.objects.create(name='Programming', slug='programming')
        child = Category.objects.create(name='Python', slug='python', parent=parent)
        
        assert child.parent == parent
        assert child in parent.children.all()
    
    def test_category_is_active(self, db):
        """Test category is_active field"""
        from apps.products.models import Category
        category = Category.objects.create(
            name='Featured',
            slug='featured',
            is_active=True
        )
        assert category.is_active is True


class TestBrand:
    """Tests for Brand model"""
    
    def test_brand_creation(self, db):
        """Test creating a brand"""
        from apps.products.models import Brand
        brand = Brand.objects.create(
            name='Samsung',
            slug='samsung',
            description='Samsung brand',
            is_active=True,
            sort_order=0
        )
        
        assert brand.name == 'Samsung'
        assert brand.slug == 'samsung'
        assert brand.description == 'Samsung brand'
        assert brand.is_active is True
        assert str(brand) == 'Samsung'
    
    def test_brand_str(self, db):
        """Test string representation of brand"""
        from apps.products.models import Brand
        brand = Brand.objects.create(name='Apple', slug='apple')
        assert str(brand) == 'Apple'
    
    def test_brand_slug_generation(self, db):
        """Test brand slug generation"""
        from apps.products.models import Brand
        brand = Brand.objects.create(name='Test Brand', slug='test-brand')
        assert brand.slug == 'test-brand'


class TestTag:
    """Tests for Tag model"""
    
    def test_tag_creation(self, db):
        """Test creating a tag"""
        from apps.products.models import Tag
        tag = Tag.objects.create(
            name='electronics',
            slug='electronics',
            description='Electronics tag',
            color='#000000'
        )
        
        assert tag.name == 'electronics'
        assert tag.slug == 'electronics'
        assert tag.description == 'Electronics tag'
        assert tag.color == '#000000'
        assert str(tag) == 'electronics'
    
    def test_tag_str(self, db):
        """Test string representation of tag"""
        from apps.products.models import Tag
        tag = Tag.objects.create(name='sale', slug='sale')
        assert str(tag) == 'sale'


class TestAttribute:
    """Tests for Attribute model"""
    
    def test_attribute_creation(self, db):
        """Test creating an attribute"""
        from apps.products.models import Attribute
        attr = Attribute.objects.create(
            name='Color',
            slug='color',
            attribute_type='select',
            description='Color attribute',
            is_filterable=True,
            is_required=False,
            is_variant=False,
            sort_order=0,
            is_active=True
        )
        
        assert attr.name == 'Color'
        assert attr.slug == 'color'
        assert attr.attribute_type == 'select'
        assert attr.is_filterable is True
        assert str(attr) == 'Color'
    
    def test_attribute_str(self, db):
        """Test string representation of attribute"""
        from apps.products.models import Attribute
        attr = Attribute.objects.create(name='Size', slug='size')
        assert str(attr) == 'Size'
    
    def test_attribute_types(self, db):
        """Test different attribute types"""
        from apps.products.models import Attribute
        
        text_attr = Attribute.objects.create(
            name='Description',
            slug='description',
            attribute_type='text'
        )
        select_attr = Attribute.objects.create(
            name='Color',
            slug='color',
            attribute_type='select'
        )
        boolean_attr = Attribute.objects.create(
            name='Featured',
            slug='featured',
            attribute_type='boolean'
        )
        
        assert text_attr.attribute_type == 'text'
        assert select_attr.attribute_type == 'select'
        assert boolean_attr.attribute_type == 'boolean'


class TestAttributeValue:
    """Tests for AttributeValue model"""
    
    def test_attribute_value_creation(self, db):
        """Test creating an attribute value"""
        from apps.products.models import Attribute, AttributeValue
        attr = Attribute.objects.create(name='Color', slug='color')
        value = AttributeValue.objects.create(
            attribute=attr,
            value='Red',
            color_code='#FF0000',
            sort_order=0,
            is_active=True
        )
        
        assert value.attribute == attr
        assert value.value == 'Red'
        assert value.color_code == '#FF0000'
        assert str(value) == 'Color: Red'
    
    def test_attribute_value_str(self, db):
        """Test string representation of attribute value"""
        from apps.products.models import Attribute, AttributeValue
        attr = Attribute.objects.create(name='Size', slug='size')
        value = AttributeValue.objects.create(attribute=attr, value='Large')
        assert str(value) == 'Size: Large'


class TestProduct:
    """Tests for Product model"""
    
    def test_product_creation(self, db):
        """Test creating a product"""
        from apps.products.models import Product, Category
        category = Category.objects.create(name='Test Category', slug='test-category')
        product = Product.objects.create(
            sku='PROD001',
            name='Test Product',
            slug='test-product',
            product_type='simple',
            short_description='Short description',
            description='Product description',
            regular_price=100.00,
            sale_price=80.00,
            cost_price=70.00,
            stock_quantity=10,
            stock_status='in_stock',
            category=category,
            is_active=True,
            is_featured=False
        )
        
        assert product.sku == 'PROD001'
        assert product.name == 'Test Product'
        assert product.slug == 'test-product'
        assert product.regular_price == 100.00
        assert product.sale_price == 80.00
        assert product.get_price() == 80.00  # Should return sale price
        assert str(product) == 'Test Product'
    
    def test_product_str(self, db):
        """Test string representation of product"""
        from apps.products.models import Product
        product = Product.objects.create(
            sku='PROD002',
            name='Another Product',
            slug='another-product',
            regular_price=50.00
        )
        assert str(product) == 'Another Product'
    
    def test_product_price_properties(self, db):
        """Test product price properties"""
        from apps.products.models import Product
        product = Product.objects.create(
            sku='PROD003',
            name='Price Test',
            slug='price-test',
            regular_price=100.00,
            sale_price=80.00
        )
        
        assert product.get_price() == 80.00
        assert product.get_discount_percentage() == 20.0
    
    def test_product_without_sale_price(self, db):
        """Test product without sale price"""
        from apps.products.models import Product
        product = Product.objects.create(
            sku='PROD004',
            name='No Sale',
            slug='no-sale',
            regular_price=100.00,
            sale_price=None
        )
        
        assert product.get_price() == 100.00
        assert product.get_discount_percentage() == 0
    
    def test_product_stock_status(self, db):
        """Test product stock status"""
        from apps.products.models import Product
        
        in_stock = Product.objects.create(
            sku='PROD005',
            name='In Stock',
            slug='in-stock',
            regular_price=50.00,
            stock_status='in_stock',
            stock_quantity=10
        )
        
        out_of_stock = Product.objects.create(
            sku='PROD006',
            name='Out of Stock',
            slug='out-of-stock',
            regular_price=50.00,
            stock_status='out_of_stock',
            stock_quantity=0
        )
        
        assert in_stock.is_in_stock() is True
        assert out_of_stock.is_in_stock() is False
    
    def test_product_low_stock(self, db):
        """Test product low stock"""
        from apps.products.models import Product
        product = Product.objects.create(
            sku='PROD007',
            name='Low Stock',
            slug='low-stock',
            regular_price=50.00,
            stock_quantity=3,
            low_stock_threshold=5
        )
        
        assert product.stock_quantity < product.low_stock_threshold
    
    def test_product_featured_flags(self, db):
        """Test product featured flags"""
        from apps.products.models import Product
        product = Product.objects.create(
            sku='PROD008',
            name='Featured Product',
            slug='featured-product',
            regular_price=50.00,
            is_featured=True,
            is_best_seller=True,
            is_new=True,
            is_on_sale=True
        )
        
        assert product.is_featured is True
        assert product.is_best_seller is True
        assert product.is_new is True
        assert product.is_on_sale is True


class TestProductImage:
    """Tests for ProductImage model"""
    
    def test_product_image_creation(self, db):
        """Test creating a product image"""
        from apps.products.models import Product, ProductImage
        product = Product.objects.create(
            sku='PROD009',
            name='Image Product',
            slug='image-product',
            regular_price=50.00
        )
        image = ProductImage.objects.create(
            product=product,
            image='test_image.jpg',
            alt_text='Test image',
            sort_order=0,
            is_featured=False
        )
        
        assert image.product == product
        assert image.alt_text == 'Test image'
        assert image.sort_order == 0
        assert str(image) == f"{product.name} - Image 0"
    
    def test_product_image_str(self, db):
        """Test string representation of product image"""
        from apps.products.models import Product, ProductImage
        product = Product.objects.create(
            sku='PROD010',
            name='Image Product 2',
            slug='image-product-2',
            regular_price=50.00
        )
        image = ProductImage.objects.create(
            product=product,
            image='test2.jpg',
            alt_text='Test 2',
            sort_order=1
        )
        assert str(image) == f"{product.name} - Image 1"


class TestProductVariant:
    """Tests for ProductVariant model"""
    
    def test_product_variant_creation(self, db):
        """Test creating a product variant"""
        from apps.products.models import Product, ProductVariant
        product = Product.objects.create(
            sku='PROD011',
            name='Variant Product',
            slug='variant-product',
            regular_price=100.00
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku='VAR001',
            name='Red Variant',
            stock_quantity=5,
            stock_status='in_stock',
            is_active=True
        )
        
        assert variant.product == product
        assert variant.sku == 'VAR001'
        assert variant.name == 'Red Variant'
        assert str(variant) == f"{product.name} - {variant.name}"
    
    def test_product_variant_str(self, db):
        """Test string representation of product variant"""
        from apps.products.models import Product, ProductVariant
        product = Product.objects.create(
            sku='PROD012',
            name='Variant Product 2',
            slug='variant-product-2',
            regular_price=100.00
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku='VAR002',
            name='Blue Variant'
        )
        assert str(variant) == f"{product.name} - {variant.name}"
    
    def test_product_variant_default(self, db):
        """Test product variant default values"""
        from apps.products.models import Product, ProductVariant
        product = Product.objects.create(
            sku='PROD013',
            name='Default Variant',
            slug='default-variant',
            regular_price=100.00
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku='VAR003',
            name='Default'
        )
        
        assert variant.stock_quantity == 0
        assert variant.stock_status == 'in_stock'
        assert variant.is_active is True


class TestProductAttribute:
    """Tests for ProductAttribute model"""
    
    def test_product_attribute_creation(self, db):
        """Test creating a product attribute"""
        from apps.products.models import Product, Attribute, ProductAttribute
        product = Product.objects.create(
            sku='PROD014',
            name='Attribute Product',
            slug='attribute-product',
            regular_price=50.00
        )
        attr = Attribute.objects.create(name='Color', slug='color')
        product_attr = ProductAttribute.objects.create(
            product=product,
            attribute=attr,
            value='Red'
        )
        
        assert product_attr.product == product
        assert product_attr.attribute == attr
        assert product_attr.value == 'Red'
        assert str(product_attr) == f"{product.name} - {attr.name}: {product_attr.value}"
    
    def test_product_attribute_str(self, db):
        """Test string representation of product attribute"""
        from apps.products.models import Product, Attribute, ProductAttribute
        product = Product.objects.create(
            sku='PROD015',
            name='Attr Product',
            slug='attr-product',
            regular_price=50.00
        )
        attr = Attribute.objects.create(name='Size', slug='size')
        product_attr = ProductAttribute.objects.create(
            product=product,
            attribute=attr,
            value='Large'
        )
        assert str(product_attr) == f"{product.name} - {attr.name}: Large"
    
    def test_product_attribute_types(self, db):
        """Test different product attribute types"""
        from apps.products.models import Product, Attribute, ProductAttribute
        product = Product.objects.create(
            sku='PROD016',
            name='Types Product',
            slug='types-product',
            regular_price=50.00
        )
        
        color_attr = Attribute.objects.create(name='Color', slug='color')
        size_attr = Attribute.objects.create(name='Size', slug='size')
        
        color_value = ProductAttribute.objects.create(
            product=product,
            attribute=color_attr,
            value='Red'
        )
        size_value = ProductAttribute.objects.create(
            product=product,
            attribute=size_attr,
            value='Large'
        )
        
        assert color_value.value == 'Red'
        assert size_value.value == 'Large'
