"""
URLs for products app.
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Store pages
    path('', views.store_home, name='home'),
    path('search/', views.search, name='search'),
    
    # Categories
    path('category/<slug:slug>/', views.category_detail, name='category'),
    
    # Brands
    path('brand/<slug:slug>/', views.brand_detail, name='brand'),
    
    # Tags
    path('tag/<slug:slug>/', views.tag_detail, name='tag'),
    
    # Products
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # AJAX endpoints
    path('ajax/quick-view/<uuid:product_id>/', views.quick_view, name='quick_view'),
    path('ajax/filter-products/', views.filter_products, name='filter_products'),
    path('ajax/load-more-products/', views.load_more_products, name='load_more_products'),
]
