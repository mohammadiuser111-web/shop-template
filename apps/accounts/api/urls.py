"""
URL configuration for Accounts API.
"""
from django.urls import path
from . import views

app_name = 'accounts_api'

urlpatterns = [
    # User endpoints
    path('users/', views.UserListAPIView.as_view(), name='user_list'),
    path('users/me/', views.UserRetrieveAPIView.as_view(), name='user_me'),
    path('users/<uuid:pk>/', views.UserRetrieveAPIView.as_view(), name='user_detail'),
    path('users/create/', views.UserCreateAPIView.as_view(), name='user_create'),
    path('users/me/update/', views.UserUpdateAPIView.as_view(), name='user_update'),
    path('users/me/delete/', views.UserDeleteAPIView.as_view(), name='user_delete'),
    
    # Authentication endpoints
    path('login/', views.UserLoginAPIView.as_view(), name='login'),
    path('logout/', views.UserLogoutAPIView.as_view(), name='logout'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain'),
    
    # Password endpoints
    path('password/change/', views.PasswordChangeAPIView.as_view(), name='password_change'),
    path('password/reset/', views.PasswordChangeAPIView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordChangeAPIView.as_view(), name='password_reset_confirm'),
    
    # OTP endpoints
    path('otp/login/', views.OTPLoginAPIView.as_view(), name='otp_login'),
    path('otp/verify/', views.OTPVerifyAPIView.as_view(), name='otp_verify'),
    
    # Profile endpoints
    path('profile/', views.UserProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    
    # Address endpoints
    path('addresses/', views.UserAddressListCreateAPIView.as_view(), name='address_list_create'),
    path('addresses/<uuid:pk>/', views.UserAddressRetrieveUpdateDestroyAPIView.as_view(), name='address_detail'),
    path('addresses/<uuid:pk>/default/', views.UserAddressSetDefaultAPIView.as_view(), name='address_set_default'),
    
    # Wishlist endpoints
    path('wishlists/', views.WishlistListCreateAPIView.as_view(), name='wishlist_list_create'),
    path('wishlists/<uuid:pk>/', views.WishlistRetrieveUpdateDestroyAPIView.as_view(), name='wishlist_detail'),
    path('wishlists/<uuid:pk>/default/', views.WishlistSetDefaultAPIView.as_view(), name='wishlist_set_default'),
    
    # Dashboard endpoint
    path('dashboard/', views.UserDashboardAPIView.as_view(), name='dashboard'),
    
    # Search endpoint
    path('search/', views.UserSearchAPIView.as_view(), name='user_search'),
]
