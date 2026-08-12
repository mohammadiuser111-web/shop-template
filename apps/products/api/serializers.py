"""
Serializers for Products API.
"""
from rest_framework import serializers
from ..models import Category, Brand, Attribute, AttributeValue, Product, ProductImage, ProductVariant, Tag, Review


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    parent = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'image',
            'icon', 'is_active', 'is_featured', 'sort_order',
            'meta_title', 'meta_description', 'meta_keywords',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer for category tree with children."""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image',
            'icon', 'is_active', 'is_featured', 'sort_order',
            'children'
        ]
    
    def get_children(self, obj):
        """Get children categories."""
        children = Category.objects.filter(parent=obj, is_active=True).order_by('sort_order')
        return CategoryTreeSerializer(children, many=True).data


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model."""
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'website', 'is_active', 'is_featured', 'sort_order',
            'meta_title', 'meta_description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class AttributeSerializer(serializers.ModelSerializer):
    """Serializer for Attribute model."""
    
    class Meta:
        model = Attribute
        fields = [
            'id', 'name', 'code', 'description', 'type',
            'is_required', 'is_filterable', 'is_variant',
            'sort_order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for AttributeValue model."""
    
    attribute = AttributeSerializer(read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=Attribute.objects.all(),
        source='attribute',
        write_only=True
    )
    
    class Meta:
        model = AttributeValue
        fields = [
            'id', 'attribute', 'attribute_id', 'value', 'color_code',
            'sort_order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    
    class Meta:
        model = Tag
        fields = [
            'id', 'name', 'slug', 'description', 'color',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'product', 'image', 'alt_text', 'is_primary',
            'sort_order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'product', 'created_at', 'updated_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant model."""
    
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'sku', 'name', 'description',
            'price', 'sale_price', 'cost_price', 'quantity',
            'weight', 'length', 'width', 'height',
            'is_active', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'product', 'created_at', 'updated_at']


class ProductVariantDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for ProductVariant with attributes."""
    
    attributes = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'sku', 'name', 'description',
            'price', 'sale_price', 'cost_price', 'quantity',
            'weight', 'length', 'width', 'height',
            'is_active', 'is_default', 'attributes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'product', 'created_at', 'updated_at']
    
    def get_attributes(self, obj):
        """Get variant attributes."""
        from apps.inventory.models import VariantAttributeValue
        attributes = VariantAttributeValue.objects.filter(variant=obj).select_related('attribute', 'attribute_value')
        return [
            {
                'attribute_id': va.attribute.id,
                'attribute_name': va.attribute.name,
                'attribute_code': va.attribute.code,
                'value_id': va.attribute_value.id,
                'value': va.attribute_value.value,
                'color_code': va.attribute_value.color_code
            }
            for va in attributes
        ]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        source='brand',
        write_only=True,
        required=False,
        allow_null=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'category_id', 'brand', 'brand_id', 'tags', 'tag_ids',
            'type', 'price', 'sale_price', 'cost_price', 'quantity',
            'sku', 'barcode', 'weight', 'length', 'width', 'height',
            'unit', 'min_quantity', 'max_quantity', 'allow_backorders',
            'is_active', 'is_featured', 'is_new', 'is_best_seller',
            'is_digital', 'digital_file', 'digital_file_name',
            'meta_title', 'meta_description', 'meta_keywords',
            'search_keywords', 'sort_order', 'created_at', 'updated_at',
            'rating', 'review_count'
        ]
        read_only_fields = ['id', 'slug', 'rating', 'review_count', 'created_at', 'updated_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Product with all relations."""
    
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantDetailSerializer(many=True, read_only=True)
    attributes = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'brand', 'tags', 'images', 'variants',
            'type', 'price', 'sale_price', 'cost_price', 'quantity',
            'sku', 'barcode', 'weight', 'length', 'width', 'height',
            'unit', 'min_quantity', 'max_quantity', 'allow_backorders',
            'is_active', 'is_featured', 'is_new', 'is_best_seller',
            'is_digital', 'digital_file', 'digital_file_name',
            'meta_title', 'meta_description', 'meta_keywords',
            'search_keywords', 'sort_order', 'attributes',
            'created_at', 'updated_at', 'rating', 'review_count'
        ]
        read_only_fields = [
            'id', 'slug', 'rating', 'review_count', 'created_at', 'updated_at',
            'category', 'brand', 'tags', 'images', 'variants', 'attributes'
        ]
    
    def get_attributes(self, obj):
        """Get product attributes."""
        from apps.inventory.models import ProductAttributeValue
        attributes = ProductAttributeValue.objects.filter(product=obj).select_related('attribute', 'value')
        return [
            {
                'attribute_id': pa.attribute.id,
                'attribute_name': pa.attribute.name,
                'attribute_code': pa.attribute.code,
                'attribute_type': pa.attribute.type,
                'value_id': pa.value.id,
                'value': pa.value.value,
                'color_code': pa.value.color_code
            }
            for pa in attributes
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description',
            'category_name', 'brand_name', 'thumbnail',
            'price', 'sale_price', 'quantity',
            'is_active', 'is_featured', 'is_new', 'is_best_seller',
            'rating', 'review_count', 'created_at'
        ]
        read_only_fields = fields
    
    def get_thumbnail(self, obj):
        """Get primary image URL."""
        primary_image = ProductImage.objects.filter(product=obj, is_primary=True).first()
        if primary_image and primary_image.image:
            return self.context['request'].build_absolute_uri(primary_image.image.url)
        return None


class ProductSearchSerializer(serializers.ModelSerializer):
    """Serializer for product search results."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description',
            'category_name', 'brand_name', 'thumbnail',
            'price', 'sale_price', 'rating', 'review_count'
        ]
        read_only_fields = fields
    
    def get_thumbnail(self, obj):
        """Get primary image URL."""
        primary_image = ProductImage.objects.filter(product=obj, is_primary=True).first()
        if primary_image and primary_image.image:
            return self.context['request'].build_absolute_uri(primary_image.image.url)
        return None


class ProductFilterSerializer(serializers.Serializer):
    """Serializer for product filter options."""
    
    categories = CategorySerializer(many=True)
    brands = BrandSerializer(many=True)
    tags = TagSerializer(many=True)
    attributes = AttributeSerializer(many=True)
    price_range = serializers.DictField()
    
    class Meta:
        fields = ['categories', 'brands', 'tags', 'attributes', 'price_range']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model (from reviews app)."""
    
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'product', 'rating', 'title', 'comment',
            'is_approved', 'is_helpful', 'helpful_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_user(self, obj):
        """Get user data."""
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'avatar': obj.user.avatar.url if obj.user.avatar else None
            }
        return None
    
    def get_product(self, obj):
        """Get product data."""
        if obj.product:
            return {
                'id': obj.product.id,
                'name': obj.product.name,
                'slug': obj.product.slug
            }
        return None
