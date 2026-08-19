"""
URL configuration for checkout app.
This is separate from orders urls to allow for different namespace.
"""
from django.urls import path, include

app_name = 'checkout'

urlpatterns = [
    path('', include('apps.orders.urls')),
]
