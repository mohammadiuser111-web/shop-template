"""
URL configuration for Products API.
"""
from django.urls import path
from . import views

app_name = 'products_api'

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListCreateAPIView.as_view(), name='category_list_create'),
    path('categories/<uuid:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category_detail'),
    path('categories/tree/', views.CategoryTreeAPIView.as_view(), name='category_tree'),
    
    # Brand endpoints
    path('brands/', views.BrandListCreateAPIView.as_view(), name='brand_list_create'),
    path('brands/<uuid:pk>/', views.BrandRetrieveUpdateDestroyAPIView.as_view(), name='brand_detail'),
    
    # Attribute endpoints
    path('attributes/', views.AttributeListCreateAPIView.as_view(), name='attribute_list_create'),
    path('attributes/<uuid:pk>/', views.AttributeRetrieveUpdateDestroyAPIView.as_view(), name='attribute_detail'),
    
    # AttributeValue endpoints
    path('attribute-values/', views.AttributeValueListCreateAPIView.as_view(), name='attribute_value_list_create'),
    path('attribute-values/<uuid:pk>/', views.AttributeValueRetrieveUpdateDestroyAPIView.as_view(), name='attribute_value_detail'),
    
    # Tag endpoints
    path('tags/', views.TagListCreateAPIView.as_view(), name='tag_list_create'),
    path('tags/<uuid:pk>/', views.TagRetrieveUpdateDestroyAPIView.as_view(), name='tag_detail'),
    
    # Product endpoints
    path('products/', views.ProductListAPIView.as_view(), name='product_list'),
    path('products/<slug:slug>/', views.ProductRetrieveAPIView.as_view(), name='product_detail'),
    path('products/create/', views.ProductCreateAPIView.as_view(), name='product_create'),
    path('products/<slug:slug>/update/', views.ProductUpdateAPIView.as_view(), name='product_update'),
    path('products/<slug:slug>/delete/', views.ProductDeleteAPIView.as_view(), name='product_delete'),
    
    # Product Image endpoints
    path('products/<slug:product_slug>/images/', views.ProductImageListCreateAPIView.as_view(), name='product_image_list_create'),
    path('products/<slug:product_slug>/images/<uuid:pk>/', views.ProductImageRetrieveUpdateDestroyAPIView.as_view(), name='product_image_detail'),
    path('products/<slug:product_slug>/images/<uuid:pk>/primary/', views.ProductImageSetPrimaryAPIView.as_view(), name='product_image_set_primary'),
    
    # Product Variant endpoints
    path('products/<slug:product_slug>/variants/', views.ProductVariantListCreateAPIView.as_view(), name='product_variant_list_create'),
    path('products/<slug:product_slug>/variants/<uuid:pk>/', views.ProductVariantRetrieveUpdateDestroyAPIView.as_view(), name='product_variant_detail'),
    
    # Search and Filter endpoints
    path('products/search/', views.ProductSearchAPIView.as_view(), name='product_search'),
    path('products/filter-options/', views.ProductFilterOptionsAPIView.as_view(), name='product_filter_options'),
    
    # Featured/New/Best Seller endpoints
    path('products/featured/', views.FeaturedProductsAPIView.as_view(), name='featured_products'),
    path('products/new/', views.NewProductsAPIView.as_view(), name='new_products'),
    path('products/best-sellers/', views.BestSellerProductsAPIView.as_view(), name='best_seller_products'),
    
    # Related Products endpoint
    path('products/<slug:product_slug>/related/', views.RelatedProductsAPIView.as_view(), name='related_products'),
]
