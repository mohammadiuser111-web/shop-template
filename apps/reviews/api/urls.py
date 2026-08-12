"""
API URLs for Reviews app.
"""
from django.urls import path
from .views import (
    # Review views
    ReviewListAPIView, ReviewRetrieveAPIView,
    ReviewCreateAPIView, ReviewUpdateAPIView,
    ReviewDestroyAPIView, ReviewApproveAPIView,
    ReviewVerifyAPIView, ReviewHelpfulAPIView,
    ReviewNotHelpfulAPIView,
    # Review Image views
    ReviewImageListAPIView, ReviewImageRetrieveAPIView,
    ReviewImageCreateAPIView, ReviewImageUpdateAPIView,
    ReviewImageDestroyAPIView,
    # Review Video views
    ReviewVideoListAPIView, ReviewVideoRetrieveAPIView,
    ReviewVideoCreateAPIView, ReviewVideoUpdateAPIView,
    ReviewVideoDestroyAPIView,
    # Review Comment views
    ReviewCommentListAPIView, ReviewCommentRetrieveAPIView,
    ReviewCommentCreateAPIView, ReviewCommentDestroyAPIView,
    # Review Helpfulness views
    ReviewHelpfulnessListAPIView, ReviewHelpfulnessCreateAPIView,
    ReviewHelpfulnessDestroyAPIView,
    # Statistics and product reviews
    ReviewStatisticsAPIView, ProductReviewsAPIView,
    RecentReviewsAPIView
)

urlpatterns = [
    # Reviews
    path('reviews/', ReviewListAPIView.as_view(), name='api-reviews-list'),
    path('reviews/recent/', RecentReviewsAPIView.as_view(), name='api-reviews-recent'),
    path('reviews/create/', ReviewCreateAPIView.as_view(), name='api-reviews-create'),
    path('reviews/<uuid:pk>/', ReviewRetrieveAPIView.as_view(), name='api-reviews-retrieve'),
    path('reviews/<uuid:pk>/update/', ReviewUpdateAPIView.as_view(), name='api-reviews-update'),
    path('reviews/<uuid:pk>/delete/', ReviewDestroyAPIView.as_view(), name='api-reviews-delete'),
    path('reviews/<uuid:pk>/approve/', ReviewApproveAPIView.as_view(), name='api-reviews-approve'),
    path('reviews/<uuid:pk>/verify/', ReviewVerifyAPIView.as_view(), name='api-reviews-verify'),
    path('reviews/<uuid:pk>/helpful/', ReviewHelpfulAPIView.as_view(), name='api-reviews-helpful'),
    path('reviews/<uuid:pk>/not-helpful/', ReviewNotHelpfulAPIView.as_view(), name='api-reviews-not-helpful'),
    
    # Product-specific reviews
    path('products/<int:product_id>/reviews/', ProductReviewsAPIView.as_view(), name='api-product-reviews'),
    path('products/<int:product_id>/reviews/statistics/', ReviewStatisticsAPIView.as_view(), name='api-product-reviews-statistics'),
    
    # Review Images
    path('reviews/<uuid:review_id>/images/', ReviewImageListAPIView.as_view(), name='api-review-images-list'),
    path('images/<uuid:pk>/', ReviewImageRetrieveAPIView.as_view(), name='api-review-images-retrieve'),
    path('images/create/', ReviewImageCreateAPIView.as_view(), name='api-review-images-create'),
    path('images/<uuid:pk>/update/', ReviewImageUpdateAPIView.as_view(), name='api-review-images-update'),
    path('images/<uuid:pk>/delete/', ReviewImageDestroyAPIView.as_view(), name='api-review-images-delete'),
    
    # Review Videos
    path('reviews/<uuid:review_id>/videos/', ReviewVideoListAPIView.as_view(), name='api-review-videos-list'),
    path('videos/<uuid:pk>/', ReviewVideoRetrieveAPIView.as_view(), name='api-review-videos-retrieve'),
    path('videos/create/', ReviewVideoCreateAPIView.as_view(), name='api-review-videos-create'),
    path('videos/<uuid:pk>/update/', ReviewVideoUpdateAPIView.as_view(), name='api-review-videos-update'),
    path('videos/<uuid:pk>/delete/', ReviewVideoDestroyAPIView.as_view(), name='api-review-videos-delete'),
    
    # Review Comments
    path('reviews/<uuid:review_id>/comments/', ReviewCommentListAPIView.as_view(), name='api-review-comments-list'),
    path('comments/<uuid:pk>/', ReviewCommentRetrieveAPIView.as_view(), name='api-review-comments-retrieve'),
    path('comments/create/', ReviewCommentCreateAPIView.as_view(), name='api-review-comments-create'),
    path('comments/<uuid:pk>/delete/', ReviewCommentDestroyAPIView.as_view(), name='api-review-comments-delete'),
    
    # Review Helpfulness
    path('reviews/<uuid:review_id>/helpfulness/', ReviewHelpfulnessListAPIView.as_view(), name='api-review-helpfulness-list'),
    path('helpfulness/create/', ReviewHelpfulnessCreateAPIView.as_view(), name='api-review-helpfulness-create'),
    path('helpfulness/<uuid:pk>/delete/', ReviewHelpfulnessDestroyAPIView.as_view(), name='api-review-helpfulness-delete'),
    
    # Statistics
    path('statistics/', ReviewStatisticsAPIView.as_view(), name='api-reviews-statistics'),
]
