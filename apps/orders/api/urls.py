"""
API URLs for Orders app.
"""
from django.urls import path
from .views import (
    # Order views
    OrderListAPIView, OrderRetrieveAPIView, OrderCreateAPIView,
    OrderUpdateAPIView, OrderCancelAPIView, OrderStatusUpdateAPIView,
    UserOrdersAPIView, UserOrderRetrieveAPIView, RecentOrdersAPIView,
    OrderStatisticsAPIView,
    # Order item views
    OrderItemListAPIView, OrderItemRetrieveAPIView,
    # Refund views
    RefundListCreateAPIView, RefundRetrieveAPIView,
)

urlpatterns = [
    # Orders
    path('', OrderListAPIView.as_view(), name='api-orders-list'),
    path('create/', OrderCreateAPIView.as_view(), name='api-orders-create'),
    path('recent/', RecentOrdersAPIView.as_view(), name='api-orders-recent'),
    path('statistics/', OrderStatisticsAPIView.as_view(), name='api-orders-statistics'),
    path('<str:order_number>/', OrderRetrieveAPIView.as_view(), name='api-orders-retrieve'),
    path('<str:order_number>/update/', OrderUpdateAPIView.as_view(), name='api-orders-update'),
    path('<str:order_number>/cancel/', OrderCancelAPIView.as_view(), name='api-orders-cancel'),
    path('<str:order_number>/status/', OrderStatusUpdateAPIView.as_view(), name='api-orders-status-update'),
    
    # User orders
    path('my/', UserOrdersAPIView.as_view(), name='api-my-orders-list'),
    path('my/<str:order_number>/', UserOrderRetrieveAPIView.as_view(), name='api-my-orders-retrieve'),
    
    # Order items
    path('<str:order_number>/items/', OrderItemListAPIView.as_view(), name='api-order-items-list'),
    path('items/<int:pk>/', OrderItemRetrieveAPIView.as_view(), name='api-order-items-retrieve'),
    
    # Refunds
    path('<str:order_number>/refunds/', RefundListCreateAPIView.as_view(), name='api-refunds-list-create'),
    path('refunds/<int:pk>/', RefundRetrieveAPIView.as_view(), name='api-refunds-retrieve'),
]
