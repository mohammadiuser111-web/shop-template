"""
API URLs for Blog app.
"""
from django.urls import path
from .views import (
    # Blog Category views
    BlogCategoryListAPIView, BlogCategoryRetrieveAPIView,
    BlogCategoryCreateAPIView, BlogCategoryUpdateAPIView,
    BlogCategoryDestroyAPIView,
    # Tag views
    TagListAPIView, TagRetrieveAPIView,
    TagCreateAPIView, TagUpdateAPIView,
    TagDestroyAPIView,
    # Article views
    ArticleListAPIView, ArticleRetrieveAPIView,
    ArticleCreateAPIView, ArticleUpdateAPIView,
    ArticleDestroyAPIView, ArticleSearchAPIView,
    # Article Image views
    ArticleImageListAPIView, ArticleImageRetrieveAPIView,
    ArticleImageCreateAPIView, ArticleImageUpdateAPIView,
    ArticleImageDestroyAPIView,
    # Article Related views
    ArticleRelatedListAPIView, ArticleRelatedCreateAPIView,
    ArticleRelatedDestroyAPIView,
    # Comment views
    CommentListAPIView, CommentRetrieveAPIView,
    CommentCreateAPIView, CommentUpdateAPIView,
    CommentDestroyAPIView, CommentApproveAPIView,
    CommentRepliesAPIView,
    # Comment Rating views
    CommentRatingCreateAPIView, CommentRatingDestroyAPIView,
    # Statistics and featured/popular articles
    BlogStatisticsAPIView, RecentArticlesAPIView,
    FeaturedArticlesAPIView, PopularArticlesAPIView
)

urlpatterns = [
    # Blog Categories
    path('categories/', BlogCategoryListAPIView.as_view(), name='api-blog-categories-list'),
    path('categories/<uuid:parent_id>/', BlogCategoryListAPIView.as_view(), name='api-blog-category-children-list'),
    path('categories/create/', BlogCategoryCreateAPIView.as_view(), name='api-blog-categories-create'),
    path('categories/<uuid:pk>/', BlogCategoryRetrieveAPIView.as_view(), name='api-blog-categories-retrieve'),
    path('categories/<uuid:pk>/update/', BlogCategoryUpdateAPIView.as_view(), name='api-blog-categories-update'),
    path('categories/<uuid:pk>/delete/', BlogCategoryDestroyAPIView.as_view(), name='api-blog-categories-delete'),
    
    # Tags
    path('tags/', TagListAPIView.as_view(), name='api-blog-tags-list'),
    path('tags/create/', TagCreateAPIView.as_view(), name='api-blog-tags-create'),
    path('tags/<uuid:pk>/', TagRetrieveAPIView.as_view(), name='api-blog-tags-retrieve'),
    path('tags/<uuid:pk>/update/', TagUpdateAPIView.as_view(), name='api-blog-tags-update'),
    path('tags/<uuid:pk>/delete/', TagDestroyAPIView.as_view(), name='api-blog-tags-delete'),
    
    # Articles
    path('articles/', ArticleListAPIView.as_view(), name='api-blog-articles-list'),
    path('articles/recent/', RecentArticlesAPIView.as_view(), name='api-blog-articles-recent'),
    path('articles/featured/', FeaturedArticlesAPIView.as_view(), name='api-blog-articles-featured'),
    path('articles/popular/', PopularArticlesAPIView.as_view(), name='api-blog-articles-popular'),
    path('articles/search/', ArticleSearchAPIView.as_view(), name='api-blog-articles-search'),
    path('articles/create/', ArticleCreateAPIView.as_view(), name='api-blog-articles-create'),
    path('articles/<uuid:pk>/', ArticleRetrieveAPIView.as_view(), name='api-blog-articles-retrieve'),
    path('articles/<uuid:pk>/update/', ArticleUpdateAPIView.as_view(), name='api-blog-articles-update'),
    path('articles/<uuid:pk>/delete/', ArticleDestroyAPIView.as_view(), name='api-blog-articles-delete'),
    
    # Category-specific articles
    path('categories/<uuid:category_id>/articles/', ArticleListAPIView.as_view(), name='api-blog-category-articles-list'),
    
    # Tag-specific articles
    path('tags/<uuid:tag_id>/articles/', ArticleListAPIView.as_view(), name='api-blog-tag-articles-list'),
    
    # Article Images
    path('articles/<uuid:article_id>/images/', ArticleImageListAPIView.as_view(), name='api-blog-article-images-list'),
    path('articles/<uuid:article_id>/images/create/', ArticleImageCreateAPIView.as_view(), name='api-blog-article-images-create'),
    path('images/<uuid:pk>/', ArticleImageRetrieveAPIView.as_view(), name='api-blog-article-images-retrieve'),
    path('images/<uuid:pk>/update/', ArticleImageUpdateAPIView.as_view(), name='api-blog-article-images-update'),
    path('images/<uuid:pk>/delete/', ArticleImageDestroyAPIView.as_view(), name='api-blog-article-images-delete'),
    
    # Article Related
    path('articles/<uuid:article_id>/related/', ArticleRelatedListAPIView.as_view(), name='api-blog-article-related-list'),
    path('articles/<uuid:article_id>/related/create/', ArticleRelatedCreateAPIView.as_view(), name='api-blog-article-related-create'),
    path('related/<uuid:pk>/delete/', ArticleRelatedDestroyAPIView.as_view(), name='api-blog-article-related-delete'),
    
    # Comments
    path('articles/<uuid:article_id>/comments/', CommentListAPIView.as_view(), name='api-blog-article-comments-list'),
    path('comments/', CommentListAPIView.as_view(), name='api-blog-comments-list'),
    path('comments/create/', CommentCreateAPIView.as_view(), name='api-blog-comments-create'),
    path('comments/<uuid:pk>/', CommentRetrieveAPIView.as_view(), name='api-blog-comments-retrieve'),
    path('comments/<uuid:pk>/update/', CommentUpdateAPIView.as_view(), name='api-blog-comments-update'),
    path('comments/<uuid:pk>/delete/', CommentDestroyAPIView.as_view(), name='api-blog-comments-delete'),
    path('comments/<uuid:pk>/approve/', CommentApproveAPIView.as_view(), name='api-blog-comments-approve'),
    
    # Comment Replies
    path('comments/<uuid:comment_id>/replies/', CommentRepliesAPIView.as_view(), name='api-blog-comment-replies-list'),
    
    # Comment Ratings
    path('comments/<uuid:comment_id>/rate/', CommentRatingCreateAPIView.as_view(), name='api-blog-comment-rate'),
    path('ratings/<uuid:pk>/delete/', CommentRatingDestroyAPIView.as_view(), name='api-blog-rating-delete'),
    
    # Statistics
    path('statistics/', BlogStatisticsAPIView.as_view(), name='api-blog-statistics'),
]
