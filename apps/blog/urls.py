"""
URL configuration for blog app.
"""
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Article views
    path('', views.article_list, name='article_list'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
    
    # Category views
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Tag views
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    
    # Comment views
    path('<slug:article_slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/rate/', views.rate_comment, name='rate_comment'),
    
    # AJAX views
    path('ajax/article/<slug:slug>/', views.get_article_ajax, name='get_article_ajax'),
    path('ajax/articles/', views.get_articles_ajax, name='get_articles_ajax'),
    
    # RSS feed
    path('feed/rss/', views.rss_feed, name='rss_feed'),
]
