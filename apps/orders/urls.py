"""
URL configuration for orders app.
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout views
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/address/', views.checkout_address, name='checkout_address'),
    path('checkout/shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    
    # Order views
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.order_list, name='order_list'),
    path('<str:order_number>/', views.order_detail, name='order_detail'),
    path('<str:order_number>/cancel/', views.order_cancel, name='order_cancel'),
    path('<str:order_number>/refund/', views.request_refund, name='request_refund'),
    path('track/<str:order_number>/', views.track_order, name='track_order'),
    
    # AJAX views
    path('ajax/shipping-cost/', views.ajax_get_shipping_cost, name='ajax_get_shipping_cost'),
]
