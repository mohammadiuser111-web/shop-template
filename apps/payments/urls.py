"""
URL configuration for payments app.
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment gateway selection
    path('select/', views.PaymentGatewaySelectView.as_view(), name='select_gateway'),
    
    # Payment process
    path('process/<str:gateway_type>/', views.PaymentProcessView.as_view(), name='process_payment'),
    path('process/', views.PaymentProcessView.as_view(), name='process_payment_default'),
    
    # Payment verification
    path('verify/<str:gateway_type>/', views.PaymentVerifyView.as_view(), name='verify_payment'),
    path('verify/', views.PaymentVerifyView.as_view(), name='verify_payment_default'),
    
    # Callback URLs for gateways
    path('callback/zarinpal/', views.ZarinpalCallbackView.as_view(), name='zarinpal_callback'),
    path('callback/idpay/', views.IDPayCallbackView.as_view(), name='idpay_callback'),
    path('callback/payir/', views.PayIRCallbackView.as_view(), name='payir_callback'),
    path('callback/nextpay/', views.NextpayCallbackView.as_view(), name='nextpay_callback'),
    
    # Wallet
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('wallet/deposit/', views.WalletDepositView.as_view(), name='wallet_deposit'),
    path('wallet/withdraw/', views.WalletWithdrawView.as_view(), name='wallet_withdraw'),
    path('wallet/transactions/', views.WalletTransactionListView.as_view(), name='wallet_transactions'),
    
    # Payment history
    path('history/', views.PaymentHistoryView.as_view(), name='payment_history'),
    path('history/<uuid:transaction_id>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    
    # Payment receipt
    path('receipt/<uuid:transaction_id>/', views.PaymentReceiptView.as_view(), name='payment_receipt'),
    
    # Webhook for payment gateways
    path('webhook/<str:gateway_type>/', views.PaymentWebhookView.as_view(), name='payment_webhook'),
]
