"""
API URL configuration for shop-template project.
"""
from django.urls import path, include

urlpatterns = [
    # Core API
    path('core/', include('apps.core.api.urls', namespace='core_api')),
    
    # Accounts API
    path('accounts/', include('apps.accounts.api.urls', namespace='accounts_api')),
    
    # Products API
    path('products/', include('apps.products.api.urls', namespace='products_api')),
    
    # Cart API
    path('cart/', include('apps.cart.api.urls', namespace='cart_api')),
    
    # Orders API
    path('orders/', include('apps.orders.api.urls', namespace='orders_api')),
    
    # Payments API
    path('payments/', include('apps.payments.api.urls', namespace='payments_api')),
    
    # Shipping API
    path('shipping/', include('apps.shipping.api.urls', namespace='shipping_api')),
    
    # Inventory API
    path('inventory/', include('apps.inventory.api.urls', namespace='inventory_api')),
    
    # Discounts API
    path('discounts/', include('apps.discounts.api.urls', namespace='discounts_api')),
    
    # Reviews API
    path('reviews/', include('apps.reviews.api.urls', namespace='reviews_api')),
    
    # Blog API
    path('blog/', include('apps.blog.api.urls', namespace='blog_api')),
    
    # Support API
    path('support/', include('apps.support.api.urls', namespace='support_api')),
    
    # Ads API
    path('ads/', include('apps.ads.api.urls', namespace='ads_api')),
    
    # Notifications API
    path('notifications/', include('apps.notifications.api.urls', namespace='notifications_api')),
]
