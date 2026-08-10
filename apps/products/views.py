"""
Views for products app.
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json


def store_home(request):
    """Store home page."""
    from .models import Product, Category, Brand
    from apps.ads.models import AdSlot
    from apps.blog.models import Article
    
    # Get featured products
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category', 'brand').prefetch_related('images')[:12]
    
    # Get new products
    new_products = Product.objects.filter(
        is_active=True,
        is_new=True
    ).select_related('category', 'brand').prefetch_related('images')[:12]
    
    # Get best sellers
    best_sellers = Product.objects.filter(
        is_active=True,
        is_best_seller=True
    ).select_related('category', 'brand').prefetch_related('images')[:12]
    
    # Get on sale products
    on_sale_products = Product.objects.filter(
        is_active=True,
        is_on_sale=True
    ).select_related('category', 'brand').prefetch_related('images')[:12]
    
    # Get categories
    categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    ).prefetch_related('children')[:10]
    
    # Get brands
    brands = Brand.objects.filter(is_active=True)[:10]
    
    # Get featured articles
    featured_articles = Article.objects.filter(
        is_active=True,
        is_featured=True,
        status='published'
    ).select_related('author')[:6]
    
    # Get ad slots
    homepage_top_ad = None
    homepage_top_slot = AdSlot.objects.filter(code='homepage_top', is_active=True).first()
    if homepage_top_slot:
        homepage_top_ad = homepage_top_slot.get_current_ad()
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'best_sellers': best_sellers,
        'on_sale_products': on_sale_products,
        'categories': categories,
        'brands': brands,
        'featured_articles': featured_articles,
        'homepage_top_ad': homepage_top_ad,
    }
    
    return render(request, 'store/home.html', context)


def category_detail(request, slug):
    """Category detail page."""
    from .models import Category, Product
    
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get all products in this category (including subcategories)
    category_ids = [category.id] + [c.id for c in category.get_all_descendants()]
    
    products = Product.objects.filter(
        is_active=True,
        category__id__in=category_ids
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Filter and sort
    products = filter_and_sort_products(request, products)
    
    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Get subcategories
    subcategories = category.get_children()
    
    # Get parent categories for breadcrumb
    ancestors = category.get_ancestors()
    
    context = {
        'category': category,
        'products': products_page,
        'subcategories': subcategories,
        'ancestors': ancestors,
    }
    
    return render(request, 'store/category.html', context)


def brand_detail(request, slug):
    """Brand detail page."""
    from .models import Brand, Product
    
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    
    products = Product.objects.filter(
        is_active=True,
        brand=brand
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Filter and sort
    products = filter_and_sort_products(request, products)
    
    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    context = {
        'brand': brand,
        'products': products_page,
    }
    
    return render(request, 'store/brand.html', context)


def tag_detail(request, slug):
    """Tag detail page."""
    from .models import Tag, Product
    
    tag = get_object_or_404(Tag, slug=slug)
    
    products = Product.objects.filter(
        is_active=True,
        tags=tag
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Filter and sort
    products = filter_and_sort_products(request, products)
    
    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    context = {
        'tag': tag,
        'products': products_page,
    }
    
    return render(request, 'store/tag.html', context)


def product_detail(request, slug):
    """Product detail page."""
    from .models import Product, ProductImage, ProductVariant, Review
    from apps.cart.forms import AddToCartForm
    from apps.reviews.models import Review as ProductReview
    
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Prefetch related data
    product = product.__class__.objects.filter(pk=product.pk).select_related(
        'category', 'brand'
    ).prefetch_related(
        'images', 'variants', 'variants__attribute_values',
        'reviews', 'reviews__user', 'related_products'
    ).first()
    
    # Get product images
    images = product.images.all().order_by('sort_order')
    
    # Get product variants
    variants = product.variants.filter(is_active=True).prefetch_related('attribute_values')
    
    # Get related products
    related_products = product.related_products.filter(is_active=True)[:8]
    
    # Get reviews
    reviews = product.reviews.filter(is_approved=True).select_related('user')[:10]
    
    # Calculate average rating
    avg_rating = product.get_rating()
    review_count = product.get_review_count()
    
    # Get upsell and cross-sell products
    upsell_products = product.upsell_products.filter(is_active=True)[:4]
    cross_sell_products = product.cross_sell_related.filter(is_active=True)[:4]
    
    # Add to cart form
    add_to_cart_form = AddToCartForm(initial={
        'product_id': product.id,
        'quantity': 1,
    })
    
    context = {
        'product': product,
        'images': images,
        'variants': variants,
        'related_products': related_products,
        'upsell_products': upsell_products,
        'cross_sell_products': cross_sell_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'add_to_cart_form': add_to_cart_form,
    }
    
    return render(request, 'store/product_detail.html', context)


def search(request):
    """Search page."""
    from .models import Product, Category, Brand
    
    query = request.GET.get('q', '')
    
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(short_description__icontains=query) | 
            Q(description__icontains=query) | 
            Q(tags__name__icontains=query) | 
            Q(category__name__icontains=query) | 
            Q(brand__name__icontains=query)
        ).distinct()
    
    # Filter and sort
    products = filter_and_sort_products(request, products)
    
    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Get popular searches
    # This would be implemented with a separate model in a real application
    popular_searches = []
    
    # Get suggestions
    suggestions = []
    if query:
        suggestions = Product.objects.filter(
            is_active=True,
            name__icontains=query
        ).values('name')[:5]
    
    context = {
        'query': query,
        'products': products_page,
        'popular_searches': popular_searches,
        'suggestions': suggestions,
    }
    
    return render(request, 'store/search.html', context)


@require_http_methods(["GET"])
def quick_view(request, product_id):
    """AJAX quick view for product."""
    from .models import Product
    
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    # Get product images
    images = product.images.all().order_by('sort_order')[:3]
    
    # Get variants
    variants = product.variants.filter(is_active=True)[:10]
    
    # Calculate rating
    avg_rating = product.get_rating()
    review_count = product.get_review_count()
    
    context = {
        'product': product,
        'images': images,
        'variants': variants,
        'avg_rating': avg_rating,
        'review_count': review_count,
    }
    
    return render(request, 'store/partials/quick_view.html', context)


@require_http_methods(["GET"])
def filter_products(request):
    """AJAX endpoint for filtering products."""
    from .models import Product
    
    # Get filter parameters
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    in_stock = request.GET.get('in_stock')
    on_sale = request.GET.get('on_sale')
    features = request.GET.getlist('features')
    
    products = Product.objects.filter(is_active=True)
    
    # Apply filters
    if category:
        products = products.filter(category__slug=category)
    
    if brand:
        products = products.filter(brand__slug=brand)
    
    if min_price:
        try:
            products = products.filter(regular_price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(regular_price__lte=float(max_price))
        except ValueError:
            pass
    
    if in_stock:
        products = products.filter(stock_quantity__gt=0)
    
    if on_sale:
        products = products.filter(is_on_sale=True)
    
    # Sort
    sort_by = request.GET.get('sort_by', 'newest')
    
    if sort_by == 'price_low':
        products = products.order_by('regular_price')
    elif sort_by == 'price_high':
        products = products.order_by('-regular_price')
    elif sort_by == 'rating':
        products = products.order_by('-reviews__rating')
    elif sort_by == 'popular':
        products = products.order_by('-view_count')
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 12)
    
    paginator = Paginator(products, per_page)
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Render partial template
    return render(request, 'store/partials/product_list.html', {
        'products': products_page,
    })


@require_http_methods(["GET"])
def load_more_products(request):
    """AJAX endpoint for loading more products."""
    from .models import Product
    
    # Get existing product IDs to exclude
    exclude_ids = request.GET.getlist('exclude_ids')
    
    products = Product.objects.filter(
        is_active=True
    ).exclude(id__in=exclude_ids)
    
    # Sort
    sort_by = request.GET.get('sort_by', 'newest')
    
    if sort_by == 'price_low':
        products = products.order_by('regular_price')
    elif sort_by == 'price_high':
        products = products.order_by('-regular_price')
    elif sort_by == 'rating':
        products = products.order_by('-reviews__rating')
    elif sort_by == 'popular':
        products = products.order_by('-view_count')
    else:
        products = products.order_by('-created_at')
    
    # Limit
    limit = request.GET.get('limit', 12)
    products = products[:int(limit)]
    
    # Render partial template
    return render(request, 'store/partials/product_list.html', {
        'products': products,
    })


def filter_and_sort_products(request, queryset):
    """Helper function to filter and sort products."""
    # Get filter parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    in_stock = request.GET.get('in_stock')
    on_sale = request.GET.get('on_sale')
    sort_by = request.GET.get('sort_by', 'newest')
    
    # Apply filters
    if min_price:
        try:
            queryset = queryset.filter(regular_price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            queryset = queryset.filter(regular_price__lte=float(max_price))
        except ValueError:
            pass
    
    if in_stock:
        queryset = queryset.filter(stock_quantity__gt=0)
    
    if on_sale:
        queryset = queryset.filter(is_on_sale=True)
    
    # Sort
    if sort_by == 'price_low':
        queryset = queryset.order_by('regular_price')
    elif sort_by == 'price_high':
        queryset = queryset.order_by('-regular_price')
    elif sort_by == 'rating':
        queryset = queryset.order_by('-reviews__rating')
    elif sort_by == 'popular':
        queryset = queryset.order_by('-view_count')
    elif sort_by == 'name_asc':
        queryset = queryset.order_by('name')
    elif sort_by == 'name_desc':
        queryset = queryset.order_by('-name')
    else:
        queryset = queryset.order_by('-created_at')
    
    return queryset
