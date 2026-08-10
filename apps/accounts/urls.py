"""
URLs for accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Password reset
    path('password/reset/', views.password_reset, name='password_reset'),
    path('password/reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password/reset/complete/', views.password_reset_complete, name='password_reset_complete'),
    
    # OTP verification
    path('verify/phone/', views.phone_verification, name='phone_verification'),
    path('verify/phone/confirm/', views.phone_verification_confirm, name='phone_verification_confirm'),
    path('verify/email/', views.email_verification, name='email_verification'),
    path('verify/email/confirm/<uidb64>/<token>/', views.email_verification_confirm, name='email_verification_confirm'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Addresses
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/<uuid:pk>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<uuid:pk>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<uuid:pk>/set-default/', views.set_default_address, name='set_default_address'),
    
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<uuid:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<uuid:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('orders/<str:order_number>/cancel/', views.order_cancel, name='order_cancel'),
    
    # Reviews
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/add/<uuid:product_id>/', views.add_review, name='add_review'),
]
