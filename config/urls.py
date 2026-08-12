"""
URL configuration for shop-template project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    path('admin-panel/', include('apps.dashboard_admin.urls', namespace='admin_panel')),
    
    # Store
    path('', include('apps.products.urls', namespace='store')),
    
    # Accounts
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    
    # Cart
    path('cart/', include('apps.cart.urls', namespace='cart')),
    
    # Orders
    path('orders/', include('apps.orders.urls', namespace='orders')),
    
    # Checkout
    path('checkout/', include('apps.orders.checkout_urls', namespace='checkout')),
    
    # Blog
    path('blog/', include('apps.blog.urls', namespace='blog')),
    
    # Support
    path('support/', include('apps.support.urls', namespace='support')),
    
    # Ads
    path('ads/', include('apps.ads.urls', namespace='ads')),
    
    # API
    path('api/', include([
        path('v1/', include('config.api_urls', namespace='api_v1')),
    ])),
    
    # Static pages
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='pages/contact.html'), name='contact'),
    path('faq/', TemplateView.as_view(template_name='pages/faq.html'), name='faq'),
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
]

# Add static and media URLs for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add debug toolbar URL for development
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# Custom error handlers
handler404 = 'apps.core.views.custom_404'
handler500 = 'apps.core.views.custom_500'
handler403 = 'apps.core.views.custom_403'
