"""
URL Configuration for Shop Template
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

# ============================================
# Main URL Patterns
# ============================================

urlpatterns = [
    # ========================================
    # Admin URLs
    # ========================================
    path('admin/', admin.site.urls),
    
    # Custom admin panel
    path('dashboard/', include('apps.dashboard_admin.urls')),
    
    # ========================================
    # Core URLs
    # ========================================
    path('', include('apps.core.urls')),
    
    # ========================================
    # Account URLs
    # ========================================
    path('accounts/', include('apps.accounts.urls')),
    
    # ========================================
    # Product URLs
    # ========================================
    path('products/', include('apps.products.urls')),
    
    # ========================================
    # Blog URLs (using API for now)
    # ========================================
    path('blog/', include('apps.blog.api.urls')),
    
    # ========================================
    # Order URLs (using API for now)
    # ========================================
    path('orders/', include('apps.orders.api.urls')),
    
    # ========================================
    # Cart URLs (using API for now)
    # ========================================
    # path('cart/', include('apps.cart.urls')),
    
    # ========================================
    # Shipping URLs (using API for now)
    # ========================================
    # path('shipping/', include('apps.shipping.urls')),
    
    # ========================================
    # Payment URLs
    # ========================================
    path('payments/', include('apps.payments.urls')),
    
    # ========================================
    # Review URLs (using API for now)
    # ========================================
    # path('reviews/', include('apps.reviews.urls')),
    
    # ========================================
    # Discount URLs (using API for now)
    # ========================================
    # path('discounts/', include('apps.discounts.urls')),
    
    # ========================================
    # Notification URLs (using API for now)
    # ========================================
    # path('notifications/', include('apps.notifications.urls')),
    
    # ========================================
    # Ads URLs
    # ========================================
    path('ads/', include('apps.ads.urls')),
    
    # ========================================
    # Inventory URLs (using API for now)
    # ========================================
    # path('inventory/', include('apps.inventory.urls')),
    
    # ========================================
    # Support URLs (using API for now)
    # ========================================
    # path('support/', include('apps.support.urls')),
    
    # ========================================
    # API URLs (commented out - need to create apps/api)
    # ========================================
    # path('api/', include('apps.api.urls')),
    
    # ========================================
    # Theme URLs (using core for now)
    # ========================================
    # path('theme/', include('apps.theme.urls')),
    
    # ========================================
    # AllAuth URLs
    # ========================================
    path('auth/', include('allauth.urls')),
]

# ============================================
# Static and Media Files (Development Only)
# ============================================

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ============================================
# Health Check Endpoint
# ============================================

urlpatterns += [
    path('health/', TemplateView.as_view(template_name='health.html'), name='health'),
]
