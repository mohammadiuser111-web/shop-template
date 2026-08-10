"""
Views for blog app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Article, BlogCategory, Tag, Comment, CommentRating
from .forms import ArticleForm, CommentForm
from apps.accounts.models import User


@require_http_methods(["GET"])
def article_list(request):
    """List all blog articles."""
    articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags', 'categories')
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(BlogCategory, slug=category_slug, is_active=True)
        articles = articles.filter(categories=category)
    
    # Filter by tag
    tag_slug = request.GET.get('tag')
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        articles = articles.filter(tags=tag)
    
    # Filter by author
    author_slug = request.GET.get('author')
    if author_slug:
        author = get_object_or_404(User, username=author_slug)
        articles = articles.filter(author=author)
    
    # Search
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(excerpt__icontains=query) | 
            Q(content__icontains=query) | 
            Q(tags__name__icontains=query) | 
            Q(categories__name__icontains=query)
        ).distinct()
    
    # Sort
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'popular':
        articles = articles.order_by('-view_count')
    elif sort_by == 'rating':
        articles = articles.order_by('-rating')
    elif sort_by == 'oldest':
        articles = articles.order_by('published_at')
    else:
        articles = articles.order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)
    
    # Get popular categories
    popular_categories = BlogCategory.objects.filter(
        is_active=True,
        articles__status='published',
        articles__published_at__lte=timezone.now()
    ).distinct()[:10]
    
    # Get popular tags
    popular_tags = Tag.objects.filter(
        articles__status='published',
        articles__published_at__lte=timezone.now()
    ).distinct()[:20]
    
    # Get featured articles
    featured_articles = Article.objects.filter(
        status='published',
        is_featured=True,
        published_at__lte=timezone.now()
    ).select_related('author').order_by('-published_at')[:5]
    
    context = {
        'articles': articles_page,
        'popular_categories': popular_categories,
        'popular_tags': popular_tags,
        'featured_articles': featured_articles,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'current_author': author_slug,
        'query': query,
        'title': _('Blog'),
    }
    return render(request, 'blog/article_list.html', context)


@require_http_methods(["GET"])
def article_detail(request, slug):
    """Article detail page."""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    # Increment view count
    article.increment_view_count()
    
    # Get related articles
    article_tags = article.tags.all()
    related_articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now(),
        tags__in=article_tags
    ).exclude(pk=article.pk).distinct()[:6]
    
    # Get comments
    comments = Comment.objects.filter(
        article=article,
        is_approved=True,
        parent__isnull=True
    ).select_related('user', 'author').prefetch_related('replies')
    
    # Comment form
    comment_form = CommentForm()
    
    # Get categories
    categories = BlogCategory.objects.filter(is_active=True)[:10]
    
    # Get tags
    tags = Tag.objects.all()[:20]
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
        'comment_form': comment_form,
        'categories': categories,
        'tags': tags,
        'title': article.title,
        'meta_title': article.meta_title or article.title,
        'meta_description': article.meta_description or article.excerpt,
    }
    return render(request, 'blog/article_detail.html', context)


@require_http_methods(["GET"])
def category_detail(request, slug):
    """Blog category detail page."""
    category = get_object_or_404(BlogCategory, slug=slug, is_active=True)
    
    articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now(),
        categories=category
    ).select_related('author').prefetch_related('tags', 'categories')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)
    
    # Get subcategories
    subcategories = category.children.filter(is_active=True)
    
    # Get parent categories for breadcrumb
    ancestors = []
    current = category.parent
    while current:
        ancestors.append(current)
        current = current.parent
    ancestors.reverse()
    
    context = {
        'category': category,
        'articles': articles_page,
        'subcategories': subcategories,
        'ancestors': ancestors,
        'title': category.name,
        'meta_title': category.meta_title or category.name,
        'meta_description': category.meta_description,
    }
    return render(request, 'blog/category_detail.html', context)


@require_http_methods(["GET"])
def tag_detail(request, slug):
    """Blog tag detail page."""
    tag = get_object_or_404(Tag, slug=slug)
    
    articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now(),
        tags=tag
    ).select_related('author').prefetch_related('tags', 'categories')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)
    
    context = {
        'tag': tag,
        'articles': articles_page,
        'title': f"Tag: {tag.name}",
    }
    return render(request, 'blog/tag_detail.html', context)


@login_required
@require_http_methods(["POST"])
def add_comment(request, article_slug):
    """Add comment to article."""
    article = get_object_or_404(Article, slug=article_slug, status='published')
    
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = Comment.objects.create(
            article=article,
            user=request.user if request.user.is_authenticated else None,
            author_name=form.cleaned_data.get('author_name'),
            author_email=form.cleaned_data.get('author_email'),
            author_website=form.cleaned_data.get('author_website'),
            content=form.cleaned_data.get('content'),
            author_ip=request.META.get('REMOTE_ADDR'),
            is_approved=False,  # Approve manually or automatically
        )
        
        messages.success(request, _('Your comment has been submitted and is awaiting approval.'))
    else:
        messages.error(request, _('Please correct the errors below.'))
    
    return redirect('blog:article_detail', slug=article_slug)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def rate_comment(request, comment_id):
    """Rate a comment (helpful/not helpful)."""
    comment = get_object_or_404(Comment, pk=comment_id, is_approved=True)
    rating = request.POST.get('rating')  # 1 = helpful, -1 = not helpful
    
    # Check if user already rated
    existing_rating = CommentRating.objects.filter(
        comment=comment,
        user=request.user
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = int(rating)
        existing_rating.save()
    else:
        # Create new rating
        CommentRating.objects.create(
            comment=comment,
            user=request.user,
            rating=int(rating)
        )
    
    # Update comment helpful counts
    comment.helpful_count = CommentRating.objects.filter(
        comment=comment,
        rating=1
    ).count()
    comment.not_helpful_count = CommentRating.objects.filter(
        comment=comment,
        rating=-1
    ).count()
    comment.save()
    
    return JsonResponse({
        'success': True,
        'helpful_count': comment.helpful_count,
        'not_helpful_count': comment.not_helpful_count,
    })


# AJAX Views
@require_http_methods(["GET"])
def get_article_ajax(request, slug):
    """Get article content via AJAX."""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    # Increment view count
    article.increment_view_count()
    
    return JsonResponse({
        'id': str(article.id),
        'title': article.title,
        'slug': article.slug,
        'excerpt': article.excerpt,
        'content': article.content,
        'featured_image': article.featured_image.url if article.featured_image else None,
        'author': article.get_author_name(),
        'published_at': article.published_at.strftime('%Y-%m-%d %H:%M:%S') if article.published_at else None,
        'view_count': article.view_count,
        'comment_count': article.comments.filter(is_approved=True).count(),
        'tags': [tag.name for tag in article.tags.all()],
        'categories': [cat.name for cat in article.categories.all()],
    })


@require_http_methods(["GET"])
def get_articles_ajax(request):
    """Get articles via AJAX (for infinite scroll)."""
    page = request.GET.get('page', 1)
    category = request.GET.get('category')
    tag = request.GET.get('tag')
    query = request.GET.get('q')
    
    articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author').prefetch_related('tags', 'categories')
    
    if category:
        articles = articles.filter(categories__slug=category)
    
    if tag:
        articles = articles.filter(tags__slug=tag)
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(excerpt__icontains=query) | 
            Q(content__icontains=query)
        ).distinct()
    
    articles = articles.order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles, 12)
    
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)
    
    articles_data = []
    for article in articles_page:
        articles_data.append({
            'id': str(article.id),
            'title': article.title,
            'slug': article.slug,
            'excerpt': article.excerpt,
            'featured_image': article.featured_image.url if article.featured_image else None,
            'author': article.get_author_name(),
            'published_at': article.published_at.strftime('%Y-%m-%d') if article.published_at else None,
            'view_count': article.view_count,
            'comment_count': article.comments.filter(is_approved=True).count(),
            'url': article.get_absolute_url(),
        })
    
    return JsonResponse({
        'articles': articles_data,
        'has_next': articles_page.has_next(),
        'has_previous': articles_page.has_previous(),
        'current_page': articles_page.number,
        'total_pages': paginator.num_pages,
    })


# RSS Feed (Optional)
@require_http_methods(["GET"])
def rss_feed(request):
    """RSS feed for blog articles."""
    from django.http import HttpResponse
    from django.utils.feedgenerator import Rss201rev2Feed
    from django.contrib.sites.models import Site
    
    articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author').order_by('-published_at')[:20]
    
    current_site = Site.objects.get_current()
    
    feed = Rss201rev2Feed(
        title=f"{current_site.name} - Blog",
        link=f"https://{current_site.domain}/blog/",
        description="Latest articles from our blog",
        language='fa-IR',
    )
    
    for article in articles:
        feed.add_item(
            title=article.title,
            link=f"https://{current_site.domain}{article.get_absolute_url()}",
            description=article.excerpt or article.content[:200],
            author_name=article.get_author_name(),
            pubdate=article.published_at,
        )
    
    response = HttpResponse(content_type='application/rss+xml')
    feed.write(response, 'utf-8')
    return response
