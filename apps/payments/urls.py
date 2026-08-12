"""
URL configuration for payments app.
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment gateway selection
    path('select/', views.payment_gateway_select, name='select_gateway'),
    
    # Payment process
    path('process/<str:gateway_type>/', views.payment_process, name='process_payment'),
    path('process/', views.payment_process, name='process_payment_default'),
    
    # Payment verification
    path('verify/<str:gateway_type>/', views.payment_process, name='verify_payment'),
    path('verify/', views.payment_process, name='verify_payment_default'),
    
    # Callback URLs for gateways
    path('callback/zarinpal/', views.zarinpal_callback, name='zarinpal_callback'),
    path('callback/idpay/', views.idpay_callback, name='idpay_callback'),
    path('callback/payir/', views.payir_callback, name='payir_callback'),
    path('callback/nextpay/', views.nextpay_callback, name='nextpay_callback'),
    
    # Wallet
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/deposit/', views.wallet_deposit, name='wallet_deposit'),
    path('wallet/withdraw/', views.wallet_withdraw, name='wallet_withdraw'),
    path('wallet/transactions/', views.wallet_transactions, name='wallet_transactions'),
    
    # Payment history
    path('history/', views.payment_history, name='payment_history'),
    path('history/<uuid:transaction_id>/', views.payment_detail, name='payment_detail'),
    
    # Payment receipt
    path('receipt/<uuid:transaction_id>/', views.payment_receipt, name='payment_receipt'),
    
    # Webhook for payment gateways
    path('webhook/<str:gateway_type>/', views.payment_webhook, name='payment_webhook'),
]
