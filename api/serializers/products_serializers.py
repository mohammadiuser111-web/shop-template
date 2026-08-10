"""
Products Serializers
Serializers for product models: Category, Brand, Attribute, AttributeValue, Tag, Product, ProductImage, ProductVariant
"""

from rest_framework import serializers
from apps.products.models import (
    Category, Brand, Attribute, AttributeValue, Tag, 
    Product, ProductImage, ProductVariant, ProductReview
)
from .reviews_serializers import ReviewListSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Category model"""
    
    parent = serializers.StringField(source='parent.name', read_only=True, allow_null=True)
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    product_count = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug', 'parent', 'image_url', 'product_count', 'children')
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
    
    def get_product_count(self, obj):
        return Product.objects.filter(categories=obj, is_published=True).count()
    
    def get_children(self, obj):
        children = Category.objects.filter(parent=obj, is_active=True)
        return CategoryListSerializer(children, many=True, context=self.context).data


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for category lists"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    product_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent_name', 'image_url', 'product_count', 'position', 'is_active', 'is_featured']
        read_only_fields = fields
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
    
    def get_product_count(self, obj):
        return Product.objects.filter(categories=obj, is_published=True).count()


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer for category tree structure"""
    
    children = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image_url', 'is_active', 'position', 'children']
        read_only_fields = fields
    
    def get_children(self, obj):
        children = Category.objects.filter(parent=obj, is_active=True)
        return CategoryTreeSerializer(children, many=True, context=self.context).data


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model"""
    
    logo_url = serializers.SerializerMethodField(read_only=True)
    product_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug', 'logo_url', 'product_count')
    
    def get_logo_url(self, obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None
    
    def get_product_count(self, obj):
        return Product.objects.filter(brand=obj, is_published=True).count()


class BrandListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for brand lists"""
    
    logo_url = serializers.SerializerMethodField(read_only=True)
    product_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo_url', 'product_count', 'is_active', 'position', 'is_featured']
        read_only_fields = fields
    
    def get_logo_url(self, obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None
    
    def get_product_count(self, obj):
        return Product.objects.filter(brand=obj, is_published=True).count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""
    
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug')


class AttributeSerializer(serializers.ModelSerializer):
    """Serializer for Attribute model"""
    
    class Meta:
        model = Attribute
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug')


class AttributeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for attribute lists"""
    
    class Meta:
        model = Attribute
        fields = ['id', 'name', 'code', 'type', 'is_required', 'is_filterable', 'position']
        read_only_fields = fields


class AttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for AttributeValue model"""
    
    attribute = AttributeSerializer(read_only=True)
    attribute_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = AttributeValue
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'attribute', 'slug')


class AttributeValueListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for attribute value lists"""
    
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    
    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute_name', 'value', 'color_code', 'position']
        read_only_fields = fields


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model"""
    
    image_url = serializers.SerializerMethodField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ProductImage
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'product', 'image_url', 'thumbnail_url')
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return self.context['request'].build_absolute_uri(obj.thumbnail.url)
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant model"""
    
    product = serializers.StringField(source='product.name', read_only=True)
    attribute_values = AttributeValueSerializer(many=True, read_only=True)
    attribute_value_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    image_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'product', 'variant_id', 'sku', 'attribute_values', 'image_url')
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None


class ProductVariantListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product variant lists"""
    
    attribute_summary = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'variant_id', 'sku', 'price', 'compare_at_price', 'quantity', 'weight', 'attribute_summary']
        read_only_fields = fields
    
    def get_attribute_summary(self, obj):
        return ", ".join([f"{av.attribute.name}: {av.value}" for av in obj.attribute_values.all()])


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for ProductReview model (through model)"""
    
    class Meta:
        model = ProductReview
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Product model"""
    
    categories = CategoryListSerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    primary_image_url = serializers.SerializerMethodField(read_only=True)
    reviews = serializers.SerializerMethodField(read_only=True)
    review_count = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    is_in_wishlist = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'slug', 'product_id', 'sku',
            'categories', 'brand', 'tags', 'images', 'variants', 'primary_image_url',
            'reviews', 'review_count', 'average_rating', 'is_in_wishlist'
        )
    
    def get_primary_image_url(self, obj):
        if obj.primary_image:
            return self.context['request'].build_absolute_uri(obj.primary_image.image.url)
        return None
    
    def get_reviews(self, obj):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(product=obj, is_approved=True).order_by('-created_at')[:5]
        return ReviewListSerializer(reviews, many=True, context=self.context).data
    
    def get_review_count(self, obj):
        from apps.reviews.models import Review
        return Review.objects.filter(product=obj, is_approved=True).count()
    
    def get_average_rating(self, obj):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(product=obj, is_approved=True)
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0
    
    def get_is_in_wishlist(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.accounts.models import Wishlist
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists"""
    
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    category_names = serializers.SerializerMethodField(read_only=True)
    primary_image_url = serializers.SerializerMethodField(read_only=True)
    review_count = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    min_price = serializers.SerializerMethodField(read_only=True)
    max_price = serializers.SerializerMethodField(read_only=True)
    is_in_wishlist = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'sku', 'name', 'slug', 'brand_name', 'category_names',
            'primary_image_url', 'price', 'compare_at_price', 'min_price', 'max_price',
            'is_published', 'is_featured', 'is_new', 'is_on_sale', 'review_count',
            'average_rating', 'is_in_wishlist', 'created_at'
        ]
        read_only_fields = fields
    
    def get_category_names(self, obj):
        return [c.name for c in obj.categories.all()]
    
    def get_primary_image_url(self, obj):
        if obj.primary_image:
            return self.context['request'].build_absolute_uri(obj.primary_image.image.url)
        return None
    
    def get_review_count(self, obj):
        from apps.reviews.models import Review
        return Review.objects.filter(product=obj, is_approved=True).count()
    
    def get_average_rating(self, obj):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(product=obj, is_approved=True)
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0
    
    def get_min_price(self, obj):
        if obj.variants.exists():
            return min(v.price for v in obj.variants.all())
        return obj.price
    
    def get_max_price(self, obj):
        if obj.variants.exists():
            return max(v.price for v in obj.variants.all())
        return obj.price
    
    def get_is_in_wishlist(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from apps.accounts.models import Wishlist
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products"""
    
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    brand_id = serializers.IntegerField(required=False, allow_null=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'sku', 'price', 'compare_at_price',
            'cost_price', 'weight', 'length', 'width', 'height', 'is_published',
            'is_featured', 'is_new', 'meta_title', 'meta_description', 'meta_keywords',
            'category_ids', 'brand_id', 'tag_ids'
        ]


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating products"""
    
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    brand_id = serializers.IntegerField(required=False, allow_null=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'sku', 'price', 'compare_at_price',
            'cost_price', 'weight', 'length', 'width', 'height', 'is_published',
            'is_featured', 'is_new', 'meta_title', 'meta_description', 'meta_keywords',
            'category_ids', 'brand_id', 'tag_ids'
        ]


class ProductVariantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating product variants"""
    
    attribute_value_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    
    class Meta:
        model = ProductVariant
        fields = ['product', 'sku', 'price', 'compare_at_price', 'quantity', 'weight', 'image', 'attribute_value_ids']


class ProductVariantUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating product variants"""
    
    attribute_value_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = ProductVariant
        fields = ['sku', 'price', 'compare_at_price', 'quantity', 'weight', 'image', 'attribute_value_ids']


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search"""
    
    query = serializers.CharField(required=False, allow_blank=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    brand_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    is_featured = serializers.BooleanField(required=False, allow_null=True)
    is_new = serializers.BooleanField(required=False, allow_null=True)
    is_on_sale = serializers.BooleanField(required=False, allow_null=True)
    in_stock = serializers.BooleanField(required=False, allow_null=True)
    sort_by = serializers.ChoiceField(
        choices=['price_asc', 'price_desc', 'newest', 'oldest', 'rating', 'name_asc', 'name_desc'],
        required=False
    )
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=20)


class ProductFilterSerializer(serializers.Serializer):
    """Serializer for product filtering"""
    
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    brands = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    price_range = serializers.ListField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2),
        required=False
    )
    attributes = serializers.DictField(required=False)
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)
    availability = serializers.BooleanField(required=False, allow_null=True)


class ProductStatsSerializer(serializers.Serializer):
    """Serializer for product statistics"""
    
    total_products = serializers.IntegerField()
    published_products = serializers.IntegerField()
    featured_products = serializers.IntegerField()
    new_products = serializers.IntegerField()
    on_sale_products = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_brands = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    products_by_category = serializers.DictField()
    products_by_brand = serializers.DictField()
    top_rated_products = serializers.ListField(child=serializers.DictField())
    best_selling_products = serializers.ListField(child=serializers.DictField())
