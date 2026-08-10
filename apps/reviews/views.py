"""
Views for reviews app.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg, Count

from .models import Review, ReviewRating, ReviewComment, ReviewHelpfulness
from .forms import ReviewForm, ReviewCommentForm
from apps.products.models import Product
from apps.orders.models import Order, OrderItem


@require_http_methods(["GET"])
def product_reviews(request, product_slug):
    """List all reviews for a product."""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    
    # Get reviews
    reviews = Review.objects.filter(
        product=product,
        is_approved=True
    ).select_related('user', 'order_item__order__user').prefetch_related(
        'review_ratings',
        'comments',
        'images'
    ).order_by('-created_at')
    
    # Filter by rating
    rating_filter = request.GET.get('rating')
    if rating_filter and rating_filter != 'all':
        reviews = reviews.filter(overall_rating=int(rating_filter))
    
    # Filter by images
    has_images = request.GET.get('has_images')
    if has_images == '1':
        reviews = reviews.filter(images__isnull=False).distinct()
    
    # Filter by verified buyers
    verified_only = request.GET.get('verified')
    if verified_only == '1':
        reviews = reviews.filter(is_verified_buyer=True)
    
    # Sort
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'helpful':
        reviews = reviews.order_by('-helpful_count', '-created_at')
    elif sort_by == 'rating_high':
        reviews = reviews.order_by('-overall_rating', '-created_at')
    elif sort_by == 'rating_low':
        reviews = reviews.order_by('overall_rating', '-created_at')
    else:
        reviews = reviews.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    
    try:
        reviews_page = paginator.page(page)
    except PageNotAnInteger:
        reviews_page = paginator.page(1)
    except EmptyPage:
        reviews_page = paginator.page(paginator.num_pages)
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
    
    # Rating distribution
    rating_distribution = []
    for i in range(5, 0, -1):
        count = reviews.filter(overall_rating=i).count()
        rating_distribution.append({
            'rating': i,
            'count': count,
            'percentage': (count / reviews.count() * 100) if reviews.count() > 0 else 0
        })
    
    # Check if user can review
    can_review = False
    user_order_item = None
    if request.user.is_authenticated:
        # Check if user has purchased this product
        user_order_item = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status__in=['completed', 'delivered']
        ).select_related('order').first()
        
        if user_order_item:
            # Check if user already reviewed
            existing_review = Review.objects.filter(
                user=request.user,
                product=product
            ).first()
            can_review = not existing_review
    
    context = {
        'product': product,
        'reviews': reviews_page,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
        'total_reviews': reviews.count(),
        'can_review': can_review,
        'user_order_item': user_order_item,
        'title': f"{_('Reviews for')} {product.name}",
        'meta_title': f"{_('Customer Reviews for')} {product.name}",
    }
    return render(request, 'reviews/product_reviews.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def add_review(request, product_slug):
    """Add a product review."""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    
    # Check if user can review this product
    user_order_item = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status__in=['completed', 'delivered']
    ).select_related('order').first()
    
    if not user_order_item:
        messages.error(request, _('You must have purchased this product to leave a review.'))
        return redirect('reviews:product_reviews', product_slug=product_slug)
    
    # Check if user already reviewed
    existing_review = Review.objects.filter(
        user=request.user,
        product=product
    ).first()
    
    if existing_review:
        messages.error(request, _('You have already reviewed this product.'))
        return redirect('reviews:product_reviews', product_slug=product_slug)
    
    if request.method == 'POST':
        form = ReviewForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            review = Review.objects.create(
                product=product,
                user=request.user,
                order_item=user_order_item,
                title=form.cleaned_data.get('title'),
                content=form.cleaned_data.get('content'),
                overall_rating=form.cleaned_data.get('overall_rating'),
                is_verified_buyer=True,
                is_approved=False,  # Approve manually or automatically
            )
            
            # Handle images
            images = request.FILES.getlist('images')
            for image in images:
                review.images.create(image=image)
            
            # Handle custom ratings (if product has custom attributes)
            custom_ratings = form.cleaned_data.get('custom_ratings', {})
            for attribute_id, rating_value in custom_ratings.items():
                ReviewRating.objects.create(
                    review=review,
                    attribute_id=attribute_id,
                    rating=rating_value
                )
            
            messages.success(request, _('Your review has been submitted and is awaiting approval.'))
            return redirect('reviews:product_reviews', product_slug=product_slug)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ReviewForm()
        # Pre-populate custom ratings based on product attributes
        # This would be handled in the form initialization
    
    context = {
        'product': product,
        'form': form,
        'order_item': user_order_item,
        'title': f"{_('Review')} {product.name}",
    }
    return render(request, 'reviews/add_review.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_review(request, review_id):
    """Edit a product review."""
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    product = review.product
    
    if request.method == 'POST':
        form = ReviewForm(data=request.POST, files=request.FILES, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = False  # Re-approve after edit
            review.save()
            
            # Handle images
            if request.FILES.getlist('images'):
                review.images.all().delete()
                images = request.FILES.getlist('images')
                for image in images:
                    review.images.create(image=image)
            
            # Handle custom ratings
            ReviewRating.objects.filter(review=review).delete()
            custom_ratings = form.cleaned_data.get('custom_ratings', {})
            for attribute_id, rating_value in custom_ratings.items():
                ReviewRating.objects.create(
                    review=review,
                    attribute_id=attribute_id,
                    rating=rating_value
                )
            
            messages.success(request, _('Your review has been updated and is awaiting approval.'))
            return redirect('reviews:product_reviews', product_slug=product.slug)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'product': product,
        'review': review,
        'form': form,
        'title': f"{_('Edit Review for')} {product.name}",
    }
    return render(request, 'reviews/edit_review.html', context)


@login_required
@require_http_methods(["POST"])
def delete_review(request, review_id):
    """Delete a product review."""
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    product_slug = review.product.slug
    
    review.delete()
    messages.success(request, _('Your review has been deleted.'))
    return redirect('reviews:product_reviews', product_slug=product_slug)


@login_required
@require_http_methods(["POST"])
def rate_review_helpfulness(request, review_id):
    """Rate a review as helpful or not helpful."""
    review = get_object_or_404(Review, pk=review_id, is_approved=True)
    is_helpful = request.POST.get('is_helpful') == 'true'
    
    # Check if user already rated
    existing_rating = ReviewHelpfulness.objects.filter(
        review=review,
        user=request.user
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.is_helpful = is_helpful
        existing_rating.save()
    else:
        # Create new rating
        ReviewHelpfulness.objects.create(
            review=review,
            user=request.user,
            is_helpful=is_helpful
        )
    
    # Update review helpful counts
    review.helpful_count = ReviewHelpfulness.objects.filter(
        review=review,
        is_helpful=True
    ).count()
    review.save()
    
    return JsonResponse({
        'success': True,
        'helpful_count': review.helpful_count,
        'is_helpful': is_helpful,
    })


@require_http_methods(["GET", "POST"])
def review_comment(request, review_id):
    """Add a comment to a review."""
    review = get_object_or_404(Review, pk=review_id, is_approved=True)
    
    if request.method == 'POST':
        form = ReviewCommentForm(data=request.POST)
        if form.is_valid():
            comment = ReviewComment.objects.create(
                review=review,
                user=request.user if request.user.is_authenticated else None,
                author_name=form.cleaned_data.get('author_name'),
                author_email=form.cleaned_data.get('author_email'),
                content=form.cleaned_data.get('content'),
                is_approved=False,  # Approve manually or automatically
            )
            
            messages.success(request, _('Your comment has been submitted.'))
            return redirect('reviews:product_reviews', product_slug=review.product.slug)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ReviewCommentForm()
    
    context = {
        'review': review,
        'form': form,
        'title': f"{_('Comment on Review')}",
    }
    return render(request, 'reviews/review_comment.html', context)


@login_required
@require_http_methods(["POST"])
def report_review(request, review_id):
    """Report a review."""
    review = get_object_or_404(Review, pk=review_id, is_approved=True)
    reason = request.POST.get('reason', '')
    
    # In a real implementation, you would create a report model
    # For now, just mark the review as reported
    review.is_reported = True
    review.report_reason = reason
    review.save()
    
    messages.success(request, _('Thank you for your report. We will review this shortly.'))
    return redirect('reviews:product_reviews', product_slug=review.product.slug)


# AJAX Views
@require_http_methods(["GET"])
def get_review_ajax(request, review_id):
    """Get review details via AJAX."""
    review = get_object_or_404(Review, pk=review_id, is_approved=True)
    
    return JsonResponse({
        'id': str(review.id),
        'title': review.title,
        'content': review.content,
        'overall_rating': review.overall_rating,
        'author': review.get_author_name(),
        'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_verified': review.is_verified_buyer,
        'helpful_count': review.helpful_count,
        'images': [img.image.url for img in review.images.all()],
        'custom_ratings': {
            rating.attribute.name if rating.attribute else str(rating.attribute_id): rating.rating
            for rating in review.review_ratings.all()
        },
    })


@require_http_methods(["GET"])
def get_reviews_summary_ajax(request, product_slug):
    """Get reviews summary for a product via AJAX."""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    
    reviews = Review.objects.filter(
        product=product,
        is_approved=True
    )
    
    avg_rating = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
    
    rating_distribution = []
    for i in range(5, 0, -1):
        count = reviews.filter(overall_rating=i).count()
        rating_distribution.append({
            'rating': i,
            'count': count,
        })
    
    return JsonResponse({
        'avg_rating': round(avg_rating, 1),
        'total_reviews': reviews.count(),
        'rating_distribution': rating_distribution,
    })


@require_http_methods(["GET"])
def load_more_reviews_ajax(request, product_slug):
    """Load more reviews via AJAX."""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    page = request.GET.get('page', 1)
    
    reviews = Review.objects.filter(
        product=product,
        is_approved=True
    ).select_related('user').prefetch_related('images', 'review_ratings').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 10)
    
    try:
        reviews_page = paginator.page(page)
    except PageNotAnInteger:
        reviews_page = paginator.page(1)
    except EmptyPage:
        reviews_page = paginator.page(paginator.num_pages)
    
    reviews_data = []
    for review in reviews_page:
        reviews_data.append({
            'id': str(review.id),
            'title': review.title,
            'content': review.content,
            'overall_rating': review.overall_rating,
            'author': review.get_author_name(),
            'created_at': review.created_at.strftime('%Y-%m-%d'),
            'is_verified': review.is_verified_buyer,
            'helpful_count': review.helpful_count,
            'images': [img.image.url for img in review.images.all()],
            'user_can_rate': request.user.is_authenticated and request.user != review.user,
            'user_has_rated': ReviewHelpfulness.objects.filter(
                review=review,
                user=request.user
            ).exists() if request.user.is_authenticated else False,
        })
    
    return JsonResponse({
        'reviews': reviews_data,
        'has_next': reviews_page.has_next(),
        'current_page': reviews_page.number,
    })
