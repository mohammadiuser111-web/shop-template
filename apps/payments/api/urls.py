"""
API URLs for Payments app.
"""
from django.urls import path
from .views import (
    # Payment Gateway views
    PaymentGatewayListAPIView, PaymentGatewayRetrieveAPIView,
    PaymentGatewayCreateAPIView, PaymentGatewayUpdateAPIView,
    PaymentGatewayDestroyAPIView, ActiveGatewaysAPIView,
    # Transaction views
    TransactionListAPIView, TransactionRetrieveAPIView,
    TransactionCreateAPIView, TransactionUpdateAPIView,
    TransactionVerifyAPIView,
    # Wallet views
    WalletRetrieveAPIView, WalletTransactionListAPIView,
    WalletDepositAPIView, WalletWithdrawAPIView,
    # Statistics views
    PaymentStatisticsAPIView
)

urlpatterns = [
    # Payment Gateways
    path('gateways/', PaymentGatewayListAPIView.as_view(), name='api-payment-gateways-list'),
    path('gateways/active/', ActiveGatewaysAPIView.as_view(), name='api-payment-gateways-active'),
    path('gateways/create/', PaymentGatewayCreateAPIView.as_view(), name='api-payment-gateways-create'),
    path('gateways/<uuid:pk>/', PaymentGatewayRetrieveAPIView.as_view(), name='api-payment-gateways-retrieve'),
    path('gateways/<uuid:pk>/update/', PaymentGatewayUpdateAPIView.as_view(), name='api-payment-gateways-update'),
    path('gateways/<uuid:pk>/delete/', PaymentGatewayDestroyAPIView.as_view(), name='api-payment-gateways-delete'),
    
    # Transactions
    path('transactions/', TransactionListAPIView.as_view(), name='api-transactions-list'),
    path('transactions/create/', TransactionCreateAPIView.as_view(), name='api-transactions-create'),
    path('transactions/verify/', TransactionVerifyAPIView.as_view(), name='api-transactions-verify'),
    path('transactions/<uuid:pk>/', TransactionRetrieveAPIView.as_view(), name='api-transactions-retrieve'),
    path('transactions/<uuid:pk>/update/', TransactionUpdateAPIView.as_view(), name='api-transactions-update'),
    
    # Wallet
    path('wallet/', WalletRetrieveAPIView.as_view(), name='api-wallet-retrieve'),
    path('wallet/transactions/', WalletTransactionListAPIView.as_view(), name='api-wallet-transactions-list'),
    path('wallet/deposit/', WalletDepositAPIView.as_view(), name='api-wallet-deposit'),
    path('wallet/withdraw/', WalletWithdrawAPIView.as_view(), name='api-wallet-withdraw'),
    
    # Statistics
    path('statistics/', PaymentStatisticsAPIView.as_view(), name='api-payments-statistics'),
]
