"""
Core views for shop-template project.
"""
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Page, SiteSetting, SocialLink, ContactInfo, Menu, MenuItem
from apps.products.models import Product, Category, ProductImage
from apps.blog.models import Article as BlogPost
from apps.ads.models import Advertisement as AdBanner, AdSlot as AdSpace


def custom_404(request, exception, template_name='errors/404.html'):
    """Custom 404 error page."""
    return render(request, template_name, status=404)


def custom_500(request, template_name='errors/500.html'):
    """Custom 500 error page."""
    return render(request, template_name, status=500)


def custom_403(request, exception, template_name='errors/403.html'):
    """Custom 403 error page."""
    return render(request, template_name, status=403)


def maintenance(request):
    """Maintenance mode page."""
    site_settings = SiteSetting.objects.filter(key='maintenance_mode').first()
    
    context = {
        'message': site_settings.value if site_settings else 'در حال حاضر سایت در حال بروزرسانی است.',
    }
    
    return render(request, 'errors/maintenance.html', context, status=503)


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'ok',
        'timestamp': str(request.timestamp) if hasattr(request, 'timestamp') else None,
    })


@require_http_methods(["GET"])
def ping(request):
    """Ping endpoint."""
    return JsonResponse({'pong': True})


def home(request):
    """Home page view."""
    # Get site settings
    site_settings = {}
    settings = SiteSetting.objects.all()
    for setting in settings:
        site_settings[setting.key] = setting.value
    
    # Get featured products
    featured_products = Product.objects.filter(is_featured=True, is_active=True).prefetch_related('images')[:8]
    
    # Get latest products
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    # Get best selling products
    best_selling_products = Product.objects.filter(is_active=True).order_by('-sales_count')[:8]
    
    # Get on sale products
    on_sale_products = Product.objects.filter(is_active=True, is_on_sale=True).prefetch_related('images')[:8]
    
    # Get categories
    categories = Category.objects.filter(is_active=True, parent=None)[:10]
    
    # Get featured categories
    featured_categories = Category.objects.filter(is_active=True, is_featured=True)[:6]
    
    # Get latest blog posts
    latest_posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')[:4]
    
    # Get banners
    header_banner = AdBanner.objects.filter(
        space__slug='header-banner',
        is_active=True
    ).order_by('sort_order').first()
    
    main_banner = AdBanner.objects.filter(
        space__slug='main-banner',
        is_active=True
    ).order_by('sort_order').first()
    
    sidebar_banners = AdBanner.objects.filter(
        space__slug='sidebar-banner',
        is_active=True
    ).order_by('sort_order')[:3]
    
    # Social links
    social_links = SocialLink.objects.filter(is_active=True).order_by('sort_order')
    
    # Contact info
    contact_info = ContactInfo.objects.filter(is_active=True).order_by('sort_order')
    
    context = {
        'site_settings': site_settings,
        'featured_products': featured_products,
        'latest_products': latest_products,
        'best_selling_products': best_selling_products,
        'on_sale_products': on_sale_products,
        'categories': categories,
        'featured_categories': featured_categories,
        'latest_posts': latest_posts,
        'header_banner': header_banner,
        'main_banner': main_banner,
        'sidebar_banners': sidebar_banners,
        'social_links': social_links,
        'contact_info': contact_info,
        'page_title': site_settings.get('site_name', 'Shop Template'),
        'meta_description': site_settings.get('site_description', ''),
        'meta_keywords': site_settings.get('site_keywords', ''),
    }
    
    return render(request, 'store/home.html', context)


def about(request):
    """About page view."""
    site_settings = {}
    settings = SiteSetting.objects.all()
    for setting in settings:
        site_settings[setting.key] = setting.value
    
    # Get about page content
    about_page = Page.objects.filter(slug='about-us').first()
    
    context = {
        'page': about_page,
        'site_settings': site_settings,
        'page_title': about_page.title if about_page else 'About Us',
        'meta_description': about_page.meta_description if about_page else '',
        'meta_keywords': about_page.meta_keywords if about_page else '',
    }
    
    return render(request, 'pages/about.html', context)


def contact(request):
    """Contact page view."""
    site_settings = {}
    settings = SiteSetting.objects.all()
    for setting in settings:
        site_settings[setting.key] = setting.value
    
    # Get contact page content
    contact_page = Page.objects.filter(slug='contact-us').first()
    
    # Contact info
    contact_info = ContactInfo.objects.filter(is_active=True).order_by('sort_order')
    
    context = {
        'page': contact_page,
        'site_settings': site_settings,
        'contact_info': contact_info,
        'page_title': contact_page.title if contact_page else 'Contact Us',
        'meta_description': contact_page.meta_description if contact_page else '',
        'meta_keywords': contact_page.meta_keywords if contact_page else '',
    }
    
    return render(request, 'pages/contact.html', context)


def custom_page(request, slug):
    """Custom page view."""
    page = get_object_or_404(Page, slug=slug, is_active=True, is_published=True)
    
    site_settings = {}
    settings = SiteSetting.objects.all()
    for setting in settings:
        site_settings[setting.key] = setting.value
    
    context = {
        'page': page,
        'site_settings': site_settings,
        'page_title': page.title,
        'meta_description': page.meta_description,
        'meta_keywords': page.meta_keywords,
    }
    
    return render(request, 'pages/custom.html', context)


def search(request):
    """Search view."""
    query = request.GET.get('q', '')
    
    # Get site settings
    site_settings = {}
    settings = SiteSetting.objects.all()
    for setting in settings:
        site_settings[setting.key] = setting.value
    
    if query:
        # Search products
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(meta_title__icontains=query) | 
            Q(meta_description__icontains=query) | 
            Q(meta_keywords__icontains=query) | 
            Q(category__name__icontains=query) | 
            Q(brand__name__icontains=query) | 
            Q(tags__name__icontains=query)
        ).filter(is_active=True).distinct().prefetch_related('images', 'category')
        
        # Search blog posts
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query) | 
            Q(meta_title__icontains=query) | 
            Q(meta_description__icontains=query) | 
            Q(meta_keywords__icontains=query) | 
            Q(tags__name__icontains=query)
        ).filter(is_published=True).distinct()
        
        # Search pages
        pages = Page.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        ).filter(is_active=True, is_published=True)
    else:
        products = Product.objects.none()
        posts = BlogPost.objects.none()
        pages = Page.objects.none()
    
    context = {
        'query': query,
        'products': products[:20],
        'posts': posts[:10],
        'pages': pages[:10],
        'site_settings': site_settings,
        'page_title': f'جستجوی: {query}' if query else 'جستجو',
    }
    
    return render(request, 'store/search.html', context)


def robots_txt(request):
    """Robots.txt view."""
    site_settings = {}
    settings = SiteSetting.objects.all()
    for setting in settings:
        site_settings[setting.key] = setting.value
    
    allow_all = site_settings.get('allow_robots', 'true').lower() == 'true'
    
    content = """User-agent: *
"""
    
    if allow_all:
        content += "Allow: /\n"
    else:
        content += "Disallow: /\n"
    
    content += "\nSitemap: " + request.build_absolute_uri('/sitemap.xml')
    
    return HttpResponse(content, content_type='text/plain')


def sitemap_xml(request):
    """Sitemap.xml view."""
    from django.urls import reverse
    
    # Get site settings
    site_settings = {}
    settings = SiteSetting.objects.all()
    for setting in settings:
        site_settings[setting.key] = setting.value
    
    site_url = request.scheme + '://' + request.get_host()
    
    # Get all URLs
    urls = []
    
    # Home page
    urls.append({'loc': site_url, 'changefreq': 'daily', 'priority': '1.0'})
    
    # About page
    about_page = Page.objects.filter(slug='about-us').first()
    if about_page:
        urls.append({'loc': site_url + '/about/', 'changefreq': 'weekly', 'priority': '0.8'})
    
    # Contact page
    contact_page = Page.objects.filter(slug='contact-us').first()
    if contact_page:
        urls.append({'loc': site_url + '/contact/', 'changefreq': 'weekly', 'priority': '0.8'})
    
    # Products
    products = Product.objects.filter(is_active=True, is_published=True)
    for product in products:
        urls.append({
            'loc': site_url + f'/products/{product.slug}/',
            'changefreq': 'weekly',
            'priority': '0.7'
        })
    
    # Categories
    categories = Category.objects.filter(is_active=True)
    for category in categories:
        urls.append({
            'loc': site_url + f'/products/category/{category.slug}/',
            'changefreq': 'weekly',
            'priority': '0.6'
        })
    
    # Blog posts
    posts = BlogPost.objects.filter(is_published=True)
    for post in posts:
        urls.append({
            'loc': site_url + f'/blog/{post.slug}/',
            'changefreq': 'weekly',
            'priority': '0.6'
        })
    
    # Custom pages
    pages = Page.objects.filter(is_active=True, is_published=True)
    for page in pages:
        urls.append({
            'loc': site_url + f'/page/{page.slug}/',
            'changefreq': 'weekly',
            'priority': '0.5'
        })
    
    # Generate XML
    xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {urls}
</urlset>
"""
    
    url_items = []
    for url in urls:
        url_items.append(
            f'    <url>\n'
            f'        <loc>{url["loc"]}</loc>\n'
            f'        <changefreq>{url["changefreq"]}</changefreq>\n'
            f'        <priority>{url["priority"]}</priority>\n'
            f'    </url>'
        )
    
    xml_content = xml_template.format(urls='\n'.join(url_items))
    
    return HttpResponse(xml_content, content_type='application/xml')
