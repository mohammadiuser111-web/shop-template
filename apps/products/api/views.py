"""
API views for Products app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, F, Count, Avg
from django.shortcuts import get_object_or_404

from ..models import Category, Brand, Attribute, AttributeValue, Product, ProductImage, ProductVariant, Tag
from .serializers import (
    CategorySerializer, CategoryTreeSerializer,
    BrandSerializer, AttributeSerializer, AttributeValueSerializer,
    TagSerializer, ProductSerializer, ProductDetailSerializer,
    ProductListSerializer, ProductSearchSerializer, ProductFilterSerializer,
    ProductVariantSerializer, ProductImageSerializer
)


# Category Views
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    """List and create categories."""
    
    queryset = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter categories."""
        queryset = super().get_queryset()
        
        # Filter by parent
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent__id=parent_id)
        
        # Filter by featured
        is_featured = self.request.query_params.get('is_featured')
        if is_featured:
            queryset = queryset.filter(is_featured=(is_featured.lower() == 'true'))
        
        # Search
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        
        return queryset


class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete category."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


class CategoryTreeAPIView(views.APIView):
    """Get category tree."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return category tree."""
        categories = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).order_by('sort_order', 'name').prefetch_related('children')
        
        serializer = CategoryTreeSerializer(categories, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Brand Views
class BrandListCreateAPIView(generics.ListCreateAPIView):
    """List and create brands."""
    
    queryset = Brand.objects.filter(is_active=True).order_by('sort_order', 'name')
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter brands."""
        queryset = super().get_queryset()
        
        # Filter by featured
        is_featured = self.request.query_params.get('is_featured')
        if is_featured:
            queryset = queryset.filter(is_featured=(is_featured.lower() == 'true'))
        
        # Search
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        
        return queryset


class BrandRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete brand."""
    
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAdminUser]


# Attribute Views
class AttributeListCreateAPIView(generics.ListCreateAPIView):
    """List and create attributes."""
    
    queryset = Attribute.objects.filter(is_active=True).order_by('sort_order', 'name')
    serializer_class = AttributeSerializer
    permission_classes = [permissions.IsAdminUser]


class AttributeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete attribute."""
    
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [permissions.IsAdminUser]


# AttributeValue Views
class AttributeValueListCreateAPIView(generics.ListCreateAPIView):
    """List and create attribute values."""
    
    serializer_class = AttributeValueSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter by attribute."""
        attribute_id = self.request.query_params.get('attribute_id')
        if attribute_id:
            return AttributeValue.objects.filter(attribute__id=attribute_id, is_active=True)
        return AttributeValue.objects.filter(is_active=True)


class AttributeValueRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete attribute value."""
    
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
    permission_classes = [permissions.IsAdminUser]


# Tag Views
class TagListCreateAPIView(generics.ListCreateAPIView):
    """List and create tags."""
    
    queryset = Tag.objects.filter(is_active=True).order_by('name')
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAdminUser]


class TagRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete tag."""
    
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAdminUser]


# Product Views
class ProductListAPIView(generics.ListAPIView):
    """List products with filtering."""
    
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Filter products."""
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                # Get all descendants
                descendants = category.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=descendants)
            except Category.DoesNotExist:
                pass
        
        # Filter by brand
        brand_slug = self.request.query_params.get('brand')
        if brand_slug:
            try:
                brand = Brand.objects.get(slug=brand_slug)
                queryset = queryset.filter(brand=brand)
            except Brand.DoesNotExist:
                pass
        
        # Filter by tag
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            try:
                tag = Tag.objects.get(slug=tag_slug)
                queryset = queryset.filter(tags=tag)
            except Tag.DoesNotExist:
                pass
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))
        
        # Filter by featured
        is_featured = self.request.query_params.get('is_featured')
        if is_featured:
            queryset = queryset.filter(is_featured=(is_featured.lower() == 'true'))
        
        # Filter by new
        is_new = self.request.query_params.get('is_new')
        if is_new:
            queryset = queryset.filter(is_new=(is_new.lower() == 'true'))
        
        # Filter by best seller
        is_best_seller = self.request.query_params.get('is_best_seller')
        if is_best_seller:
            queryset = queryset.filter(is_best_seller=(is_best_seller.lower() == 'true'))
        
        # Filter by in stock
        in_stock = self.request.query_params.get('in_stock')
        if in_stock:
            queryset = queryset.filter(quantity__gt=0)
        
        # Search
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(short_description__icontains=query) | 
                Q(description__icontains=query) | 
                Q(search_keywords__icontains=query)
            )
        
        # Sorting
        sort_by = self.request.query_params.get('sort_by', '-created_at')
        sort_options = {
            'name_asc': 'name',
            'name_desc': '-name',
            'price_asc': 'price',
            'price_desc': '-price',
            'rating': '-rating',
            'newest': '-created_at',
            'oldest': 'created_at',
            'featured': '-is_featured',
        }
        if sort_by in sort_options:
            queryset = queryset.order_by(sort_options[sort_by])
        
        return queryset.select_related('category', 'brand').prefetch_related('tags', 'images')


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve product details."""
    
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class ProductCreateAPIView(generics.CreateAPIView):
    """Create a new product (admin only)."""
    
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]


class ProductUpdateAPIView(generics.UpdateAPIView):
    """Update product (admin only)."""
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'


class ProductDeleteAPIView(generics.DestroyAPIView):
    """Delete product (admin only)."""
    
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'


# Product Image Views
class ProductImageListCreateAPIView(generics.ListCreateAPIView):
    """List and create product images."""
    
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Get product images."""
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)
        return ProductImage.objects.filter(product=product).order_by('sort_order')
    
    def perform_create(self, serializer):
        """Create image for product."""
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)
        serializer.save(product=product)


class ProductImageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete product image."""
    
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]


class ProductImageSetPrimaryAPIView(views.APIView):
    """Set an image as primary."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, product_slug, pk):
        """Set image as primary."""
        product = get_object_or_404(Product, slug=product_slug)
        image = get_object_or_404(ProductImage, pk=pk, product=product)
        
        # Reset all primary images for this product
        ProductImage.objects.filter(product=product).update(is_primary=False)
        
        # Set this as primary
        image.is_primary = True
        image.save()
        
        serializer = ProductImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Product Variant Views
class ProductVariantListCreateAPIView(generics.ListCreateAPIView):
    """List and create product variants."""
    
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Get product variants."""
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)
        return ProductVariant.objects.filter(product=product).order_by('-is_default')
    
    def perform_create(self, serializer):
        """Create variant for product."""
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)
        serializer.save(product=product)


class ProductVariantRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete product variant."""
    
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAdminUser]


# Search Views
class ProductSearchAPIView(views.APIView):
    """Search products."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Search products."""
        queryset = Product.objects.filter(is_active=True)
        
        query = request.query_params.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(short_description__icontains=query) | 
                Q(description__icontains=query) | 
                Q(search_keywords__icontains=query) | 
                Q(tags__name__icontains=query)
            ).distinct()
        
        # Apply filters
        category = request.query_params.get('category')
        if category:
            try:
                category = Category.objects.get(slug=category)
                descendants = category.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=descendants)
            except Category.DoesNotExist:
                pass
        
        brand = request.query_params.get('brand')
        if brand:
            try:
                brand = Brand.objects.get(slug=brand)
                queryset = queryset.filter(brand=brand)
            except Brand.DoesNotExist:
                pass
        
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        products = queryset[start:end]
        
        serializer = ProductSearchSerializer(
            products,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data,
            'page': page,
            'page_size': page_size,
            'total_pages': (queryset.count() + page_size - 1) // page_size
        }, status=status.HTTP_200_OK)


# Filter Options View
class ProductFilterOptionsAPIView(views.APIView):
    """Get product filter options."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return filter options."""
        # Get active categories
        categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by('sort_order')
        
        # Get active brands
        brands = Brand.objects.filter(is_active=True).order_by('sort_order')
        
        # Get active tags
        tags = Tag.objects.filter(is_active=True).order_by('name')
        
        # Get filterable attributes
        attributes = Attribute.objects.filter(is_active=True, is_filterable=True).order_by('sort_order')
        
        # Get price range
        products = Product.objects.filter(is_active=True)
        price_range = {
            'min': products.aggregate(min_price=F('price'))['min_price'] or 0,
            'max': products.aggregate(max_price=F('price'))['max_price'] or 0
        }
        
        data = {
            'categories': CategorySerializer(categories, many=True, context={'request': request}).data,
            'brands': BrandSerializer(brands, many=True, context={'request': request}).data,
            'tags': TagSerializer(tags, many=True, context={'request': request}).data,
            'attributes': AttributeSerializer(attributes, many=True).data,
            'price_range': price_range
        }
        
        serializer = ProductFilterSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Featured Products View
class FeaturedProductsAPIView(views.APIView):
    """Get featured products."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return featured products."""
        limit = int(request.query_params.get('limit', 10))
        
        products = Product.objects.filter(
            is_active=True,
            is_featured=True
        ).order_by('-created_at')[:limit]
        
        serializer = ProductListSerializer(
            products,
            many=True,
            context={'request': request}
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)


# New Products View
class NewProductsAPIView(views.APIView):
    """Get new products."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return new products."""
        limit = int(request.query_params.get('limit', 10))
        
        products = Product.objects.filter(
            is_active=True,
            is_new=True
        ).order_by('-created_at')[:limit]
        
        serializer = ProductListSerializer(
            products,
            many=True,
            context={'request': request}
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)


# Best Seller Products View
class BestSellerProductsAPIView(views.APIView):
    """Get best seller products."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return best seller products."""
        limit = int(request.query_params.get('limit', 10))
        
        products = Product.objects.filter(
            is_active=True,
            is_best_seller=True
        ).order_by('-rating', '-created_at')[:limit]
        
        serializer = ProductListSerializer(
            products,
            many=True,
            context={'request': request}
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)


# Related Products View
class RelatedProductsAPIView(views.APIView):
    """Get related products."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, product_slug):
        """Return related products."""
        product = get_object_or_404(Product, slug=product_slug, is_active=True)
        limit = int(request.query_params.get('limit', 6))
        
        # Get products from same category
        related = Product.objects.filter(
            is_active=True,
            category=product.category
        ).exclude(id=product.id).order_by('-rating', '-created_at')[:limit]
        
        serializer = ProductListSerializer(
            related,
            many=True,
            context={'request': request}
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)
