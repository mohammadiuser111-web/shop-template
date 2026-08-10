"""
Products API Views
ViewSets and APIViews for products models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.products.models import (
    Category, Brand, Tag, Attribute, AttributeValue, 
    Product, ProductImage, ProductVariant
)
from api.serializers.products_serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CategoryTreeSerializer,
    BrandSerializer,
    BrandListSerializer,
    TagSerializer,
    AttributeSerializer,
    AttributeListSerializer,
    AttributeValueSerializer,
    AttributeValueListSerializer,
    ProductImageSerializer,
    ProductVariantSerializer,
    ProductVariantListSerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
    ProductVariantCreateSerializer,
    ProductVariantUpdateSerializer,
    ProductSearchSerializer,
    ProductFilterSerializer,
    ProductStatsSerializer,
)
from api.pagination import CustomPageNumberPagination


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model"""
    
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(
            categories=category,
            is_published=True
        ).order_by('-created_at')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        categories = Category.objects.filter(parent__isnull=True, is_active=True)
        serializer = CategoryTreeSerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryTreeAPIView(APIView):
    """APIView for category tree structure"""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        categories = Category.objects.filter(parent__isnull=True, is_active=True)
        serializer = CategoryTreeSerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):
    """ViewSet for Brand model"""
    
    serializer_class = BrandSerializer
    queryset = Brand.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_featured']
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BrandListSerializer
        return BrandSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        brand = self.get_object()
        products = Product.objects.filter(
            brand=brand,
            is_published=True
        ).order_by('-created_at')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for Tag model"""
    
    serializer_class = TagSerializer
    queryset = Tag.objects.all().order_by('name')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        tag = self.get_object()
        products = Product.objects.filter(
            tags=tag,
            is_published=True
        ).order_by('-created_at')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class AttributeViewSet(viewsets.ModelViewSet):
    """ViewSet for Attribute model"""
    
    serializer_class = AttributeSerializer
    queryset = Attribute.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_required', 'is_filterable']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AttributeListSerializer
        return AttributeSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def values(self, request, pk=None):
        attribute = self.get_object()
        values = AttributeValue.objects.filter(attribute=attribute)
        serializer = AttributeValueListSerializer(values, many=True, context={'request': request})
        return Response(serializer.data)


class AttributeValueViewSet(viewsets.ModelViewSet):
    """ViewSet for AttributeValue model"""
    
    serializer_class = AttributeValueSerializer
    queryset = AttributeValue.objects.all().order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['attribute', 'is_active']
    search_fields = ['value', 'slug']
    ordering_fields = ['value', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AttributeValueListSerializer
        return AttributeValueSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class ProductImageViewSet(viewsets.ModelViewSet):
    """ViewSet for ProductImage model"""
    
    serializer_class = ProductImageSerializer
    queryset = ProductImage.objects.all().order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['product', 'is_primary']
    search_fields = ['alt_text']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def perform_create(self, serializer):
        product_id = self.request.data.get('product_id')
        product = Product.objects.get(id=product_id)
        serializer.save(product=product)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """ViewSet for ProductVariant model"""
    
    serializer_class = ProductVariantSerializer
    queryset = ProductVariant.objects.all().order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'is_active']
    search_fields = ['sku', 'variant_id']
    ordering_fields = ['price', 'position', 'quantity']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductVariantListSerializer
        elif self.action == 'create':
            return ProductVariantCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ProductVariantUpdateSerializer
        return ProductVariantSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model"""
    
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_published=True).order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'categories', 'brand', 'tags', 'is_published', 
        'is_featured', 'is_new', 'is_on_sale', 'is_active'
    ]
    search_fields = ['name', 'description', 'short_description', 'sku', 'meta_title', 'meta_keywords']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at', 'view_count']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ProductUpdateSerializer
        return ProductSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))
        
        # Filter by category slug
        category_slug = self.request.query_params.get('category_slug')
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
        
        # Filter by brand slug
        brand_slug = self.request.query_params.get('brand_slug')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Filter by tag slug
        tag_slug = self.request.query_params.get('tag_slug')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        return queryset.distinct()
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        product = self.get_object()
        product.view_count += 1
        product.save()
        return Response({'status': 'success', 'view_count': product.view_count})
    
    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        product = self.get_object()
        variants = ProductVariant.objects.filter(product=product, is_active=True)
        serializer = ProductVariantListSerializer(variants, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        product = self.get_object()
        images = ProductImage.objects.filter(product=product)
        serializer = ProductImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        queryset = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new(self, request):
        queryset = self.get_queryset().filter(is_new=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        queryset = self.get_queryset().filter(is_on_sale=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class ProductSearchAPIView(APIView):
    """APIView for product search"""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        from django.db.models import Q
        
        query = request.query_params.get('q', '')
        category_ids = request.query_params.getlist('category_ids')
        brand_ids = request.query_params.getlist('brand_ids')
        tag_ids = request.query_params.getlist('tag_ids')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        is_featured = request.query_params.get('is_featured')
        is_new = request.query_params.get('is_new')
        is_on_sale = request.query_params.get('is_on_sale')
        sort_by = request.query_params.get('sort_by', 'newest')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        queryset = Product.objects.filter(is_published=True)
        
        # Apply filters
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) | 
                Q(short_description__icontains=query) | 
                Q(sku__icontains=query) | 
                Q(meta_keywords__icontains=query)
            )
        
        if category_ids:
            queryset = queryset.filter(categories__id__in=category_ids)
        
        if brand_ids:
            queryset = queryset.filter(brand_id__in=brand_ids)
        
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids)
        
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))
        
        if is_featured:
            queryset = queryset.filter(is_featured=True)
        
        if is_new:
            queryset = queryset.filter(is_new=True)
        
        if is_on_sale:
            queryset = queryset.filter(is_on_sale=True)
        
        # Apply sorting
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        elif sort_by == 'name_asc':
            queryset = queryset.order_by('name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        page_queryset = queryset.distinct()[start:end]
        
        serializer = ProductListSerializer(page_queryset, many=True, context={'request': request})
        
        return Response({
            'results': serializer.data,
            'count': queryset.count(),
            'page': page,
            'page_size': page_size,
            'total_pages': (queryset.count() + page_size - 1) // page_size
        })


class ProductFilterAPIView(APIView):
    """APIView for product filtering options"""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        categories = Category.objects.filter(is_active=True).order_by('name')
        brands = Brand.objects.filter(is_active=True).order_by('name')
        tags = Tag.objects.filter(is_active=True).order_by('name')
        
        # Get price range
        from django.db.models import Min, Max
        price_stats = Product.objects.filter(is_published=True).aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        return Response({
            'categories': CategoryListSerializer(categories, many=True, context={'request': request}).data,
            'brands': BrandListSerializer(brands, many=True, context={'request': request}).data,
            'tags': TagSerializer(tags, many=True, context={'request': request}).data,
            'price_range': {
                'min': float(price_stats['min_price']) if price_stats['min_price'] else 0,
                'max': float(price_stats['max_price']) if price_stats['max_price'] else 1000
            }
        })


class ProductStatsAPIView(APIView):
    """APIView for product statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from apps.orders.models import Order, OrderItem
        from apps.reviews.models import Review
        from django.db.models import Count, Sum, Avg
        
        stats = {
            'total_products': Product.objects.count(),
            'published_products': Product.objects.filter(is_published=True).count(),
            'featured_products': Product.objects.filter(is_featured=True).count(),
            'new_products': Product.objects.filter(is_new=True).count(),
            'on_sale_products': Product.objects.filter(is_on_sale=True).count(),
            'total_categories': Category.objects.count(),
            'total_brands': Brand.objects.count(),
            'total_reviews': Review.objects.filter(is_approved=True).count(),
            'average_rating': Review.objects.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0,
            'products_by_category': {},
            'products_by_brand': {},
            'top_rated_products': [],
            'best_selling_products': []
        }
        
        # Products by category
        category_stats = Product.objects.filter(is_published=True).values('categories__name').annotate(
            count=Count('id')
        )
        for stat in category_stats:
            stats['products_by_category'][stat['categories__name']] = stat['count']
        
        # Products by brand
        brand_stats = Product.objects.filter(is_published=True).values('brand__name').annotate(
            count=Count('id')
        )
        for stat in brand_stats:
            stats['products_by_brand'][stat['brand__name']] = stat['count']
        
        # Top rated products
        top_rated = Product.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(
            is_published=True,
            reviews__is_approved=True
        ).order_by('-avg_rating')[:10]
        
        for product in top_rated:
            stats['top_rated_products'].append({
                'id': product.id,
                'name': product.name,
                'average_rating': float(product.avg_rating) if product.avg_rating else 0
            })
        
        # Best selling products
        best_selling = OrderItem.objects.values('product__id', 'product__name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')[:10]
        
        for item in best_selling:
            stats['best_selling_products'].append({
                'id': item['product__id'],
                'name': item['product__name'],
                'total_sold': item['total_quantity']
            })
        
        serializer = ProductStatsSerializer(stats)
        return Response(serializer.data)
