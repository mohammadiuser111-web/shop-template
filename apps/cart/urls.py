"""
URL configuration for cart app.
"""
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Cart views
    path('', views.view_cart, name='view'),
    path('add/', views.add_to_cart, name='add'),
    path('update/<int:item_id>/', views.update_cart_item, name='update'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove'),
    path('clear/', views.clear_cart, name='clear'),
    
    # Coupon views
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    
    # AJAX views
    path('summary/', views.get_cart_summary, name='summary'),
]
