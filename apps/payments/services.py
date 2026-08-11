"""
Payment gateway services for shop-template project.
Implements integration with various Iranian payment gateways.
"""
import requests
import json
import hashlib
import hmac
import uuid
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .models import PaymentGateway, Transaction
from apps.orders.models import Order


class PaymentGatewayBase:
    """Base class for all payment gateways."""
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.config = gateway.config
    
    def get_redirect_url(self, transaction):
        """Get redirect URL for payment."""
        raise NotImplementedError("Subclasses must implement get_redirect_url")
    
    def verify_payment(self, request_data):
        """Verify payment from callback."""
        raise NotImplementedError("Subclasses must implement verify_payment")
    
    def create_transaction(self, order, user, amount, currency='IRR', **kwargs):
        """Create a new transaction."""
        transaction_id = str(uuid.uuid4())
        
        transaction = Transaction.objects.create(
            transaction_id=transaction_id,
            user=user,
            order=order,
            gateway=self.gateway,
            amount=amount,
            currency=currency,
            transaction_type='purchase',
            status='pending',
            customer_name=user.get_full_name() if user else '',
            customer_email=user.email if user else '',
            customer_phone=user.phone_number if hasattr(user, 'phone_number') and user.phone_number else '',
            **kwargs
        )
        
        return transaction
    
    def update_transaction(self, transaction, status, **kwargs):
        """Update transaction status."""
        transaction.status = status
        for key, value in kwargs.items():
            setattr(transaction, key, value)
        transaction.save()
        return transaction


class ZarinpalGateway(PaymentGatewayBase):
    """Zarinpal payment gateway integration."""
    
    GATEWAY_NAME = 'zarinpal'
    SANDBOX_URL = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json'
    PRODUCTION_URL = 'https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json'
    VERIFY_URL = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json'
    PRODUCTION_VERIFY_URL = 'https://www.zarinpal.com/pg/rest/WebGate/PaymentVerification.json'
    
    def __init__(self, gateway):
        super().__init__(gateway)
        self.merchant_id = self.config.get('MERCHANT_ID', '')
        self.sandbox = self.config.get('SANDBOX', True)
    
    def get_redirect_url(self, transaction):
        """Generate Zarinpal payment URL."""
        callback_url = self._get_callback_url()
        
        data = {
            'MerchantID': self.merchant_id,
            'Amount': int(transaction.amount),
            'CallbackURL': callback_url,
            'Description': f'پرداخت سفارش #{transaction.order.code if transaction.order else transaction.transaction_id}',
            'Metadata': json.dumps({
                'transaction_id': transaction.transaction_id,
                'order_id': transaction.order.id if transaction.order else None
            }),
            'Mobile': transaction.customer_phone or '',
            'Email': transaction.customer_email or '',
        }
        
        headers = {'Content-Type': 'application/json'}
        
        if self.sandbox:
            response = requests.post(self.SANDBOX_URL, json=data, headers=headers)
        else:
            response = requests.post(self.PRODUCTION_URL, json=data, headers=headers)
        
        result = response.json()
        
        if result.get('Status') == 100:
            authority = result['Authority']
            transaction.gateway_reference = authority
            transaction.save()
            
            if self.sandbox:
                return f'https://sandbox.zarinpal.com/pg/StartPay/{authority}'
            else:
                return f'https://www.zarinpal.com/pg/StartPay/{authority}'
        else:
            error_code = result.get('Status', -1)
            error_message = result.get('Message', 'خطا در اتصال به درگاه')
            transaction.error_code = str(error_code)
            transaction.error_message = error_message
            transaction.status = 'failed'
            transaction.save()
            return None
    
    def verify_payment(self, request_data):
        """Verify Zarinpal payment."""
        authority = request_data.get('Authority')
        status = request_data.get('Status')
        
        if not authority or status != 'OK':
            return None, {'success': False, 'message': 'پرداخت ناموفق بود'}
        
        # Find transaction by authority
        transaction = Transaction.objects.filter(
            gateway_reference=authority,
            gateway=self.gateway,
            status='pending'
        ).first()
        
        if not transaction:
            return None, {'success': False, 'message': 'تراکنش یافت نشد'}
        
        data = {
            'MerchantID': self.merchant_id,
            'Authority': authority,
            'Amount': int(transaction.amount),
        }
        
        headers = {'Content-Type': 'application/json'}
        
        if self.sandbox:
            response = requests.post(self.VERIFY_URL, json=data, headers=headers)
        else:
            response = requests.post(self.PRODUCTION_VERIFY_URL, json=data, headers=headers)
        
        result = response.json()
        
        if result.get('Status') == 100:
            ref_id = result.get('RefID', '')
            transaction.gateway_reference = ref_id
            transaction.gateway_response = result
            transaction.status = 'success'
            transaction.completed_at = timezone.now()
            transaction.save()
            
            return transaction, {
                'success': True,
                'ref_id': ref_id,
                'message': 'پرداخت با موفقیت انجام شد'
            }
        else:
            error_code = result.get('Status', -1)
            error_message = result.get('Message', 'تایید پرداخت ناموفق بود')
            transaction.error_code = str(error_code)
            transaction.error_message = error_message
            transaction.status = 'failed'
            transaction.save()
            
            return transaction, {
                'success': False,
                'message': error_message
            }
    
    def _get_callback_url(self):
        """Get callback URL for Zarinpal."""
        return f"{settings.SITE_URL.rstrip('/')}/payments/callback/zarinpal/"


class IDPayGateway(PaymentGatewayBase):
    """IDPay payment gateway integration."""
    
    GATEWAY_NAME = 'idpay'
    SANDBOX_URL = 'https://api.idpay.ir/v1.1/payment'
    PRODUCTION_URL = 'https://api.idpay.ir/v1.1/payment'
    VERIFY_URL = 'https://api.idpay.ir/v1.1/payment/verify'
    INQUIRY_URL = 'https://api.idpay.ir/v1.1/payment/inquiry'
    
    def __init__(self, gateway):
        super().__init__(gateway)
        self.api_key = self.config.get('API_KEY', '')
        self.sandbox = self.config.get('SANDBOX', True)
    
    def get_redirect_url(self, transaction):
        """Generate IDPay payment URL."""
        callback_url = self._get_callback_url()
        
        data = {
            'order_id': str(transaction.transaction_id),
            'amount': int(transaction.amount),
            'name': transaction.customer_name or '',
            'phone': transaction.customer_phone or '',
            'mail': transaction.customer_email or '',
            'desc': f'پرداخت سفارش #{transaction.order.code if transaction.order else transaction.transaction_id}',
            'callback': callback_url,
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': self.api_key,
            'X-SANDBOX': '1' if self.sandbox else '0',
        }
        
        response = requests.post(self.SANDBOX_URL if self.sandbox else self.PRODUCTION_URL, 
                               json=data, headers=headers)
        
        result = response.json()
        
        if result.get('status') == 10:
            link = result.get('link')
            transaction.gateway_reference = result.get('id')
            transaction.save()
            return link
        else:
            error_code = result.get('status', -1)
            error_message = result.get('message', 'خطا در اتصال به درگاه')
            transaction.error_code = str(error_code)
            transaction.error_message = error_message
            transaction.status = 'failed'
            transaction.save()
            return None
    
    def verify_payment(self, request_data):
        """Verify IDPay payment."""
        order_id = request_data.get('order_id')
        id = request_data.get('id')
        status = request_data.get('status')
        
        if status != '10':
            return None, {'success': False, 'message': 'پرداخت ناموفق بود'}
        
        transaction = Transaction.objects.filter(
            transaction_id=order_id,
            gateway=self.gateway,
            status='pending'
        ).first()
        
        if not transaction:
            return None, {'success': False, 'message': 'تراکنش یافت نشد'}
        
        data = {
            'id': id,
            'order_id': order_id,
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': self.api_key,
            'X-SANDBOX': '1' if self.sandbox else '0',
        }
        
        response = requests.post(self.VERIFY_URL, json=data, headers=headers)
        
        result = response.json()
        
        if result.get('status') in [100, 101]:
            transaction.gateway_reference = id
            transaction.gateway_response = result
            transaction.status = 'success'
            transaction.completed_at = timezone.now()
            transaction.save()
            
            return transaction, {
                'success': True,
                'message': 'پرداخت با موفقیت تایید شد'
            }
        else:
            error_code = result.get('status', -1)
            error_message = result.get('message', 'تایید پرداخت ناموفق بود')
            transaction.error_code = str(error_code)
            transaction.error_message = error_message
            transaction.status = 'failed'
            transaction.save()
            
            return transaction, {
                'success': False,
                'message': error_message
            }
    
    def _get_callback_url(self):
        """Get callback URL for IDPay."""
        return f"{settings.SITE_URL.rstrip('/')}/payments/callback/idpay/"


class PayIRGateway(PaymentGatewayBase):
    """Pay.ir payment gateway integration."""
    
    GATEWAY_NAME = 'payir'
    SANDBOX_URL = 'https://pay.ir/pg/send'
    PRODUCTION_URL = 'https://pay.ir/pg/send'
    VERIFY_URL = 'https://pay.ir/pg/verify'
    
    def __init__(self, gateway):
        super().__init__(gateway)
        self.api_key = self.config.get('API_KEY', '')
        self.sandbox = self.config.get('SANDBOX', True)
    
    def get_redirect_url(self, transaction):
        """Generate Pay.ir payment URL."""
        callback_url = self._get_callback_url()
        
        data = {
            'api': self.api_key,
            'amount': int(transaction.amount),
            'redirect': callback_url,
            'mobile': transaction.customer_phone or '',
            'factorNumber': str(transaction.transaction_id),
            'description': f'پرداخت سفارش #{transaction.order.code if transaction.order else transaction.transaction_id}',
        }
        
        response = requests.post(self.SANDBOX_URL if self.sandbox else self.PRODUCTION_URL, 
                               data=data)
        
        result = response.text
        
        if 'token' in result:
            token = result.split(',')[0].replace('token=', '')
            transaction.gateway_reference = token
            transaction.save()
            return f'https://pay.ir/pg/{token}'
        else:
            transaction.error_message = result
            transaction.status = 'failed'
            transaction.save()
            return None
    
    def verify_payment(self, request_data):
        """Verify Pay.ir payment."""
        token = request_data.get('token')
        status = request_data.get('status')
        
        if status != '1':
            return None, {'success': False, 'message': 'پرداخت ناموفق بود'}
        
        transaction = Transaction.objects.filter(
            gateway_reference=token,
            gateway=self.gateway,
            status='pending'
        ).first()
        
        if not transaction:
            return None, {'success': False, 'message': 'تراکنش یافت نشد'}
        
        data = {
            'api': self.api_key,
            'token': token,
        }
        
        response = requests.post(self.VERIFY_URL, data=data)
        
        result = response.text
        
        if 'verify' in result and 'true' in result:
            parts = result.split(',')
            verify_result = {p.split('=')[0]: p.split('=')[1] for p in parts}
            
            if verify_result.get('verify') == 'true':
                transaction.gateway_reference = token
                transaction.gateway_response = verify_result
                transaction.status = 'success'
                transaction.completed_at = timezone.now()
                transaction.save()
                
                return transaction, {
                    'success': True,
                    'message': 'پرداخت با موفقیت تایید شد'
                }
        
        transaction.error_message = result
        transaction.status = 'failed'
        transaction.save()
        
        return transaction, {
            'success': False,
            'message': 'تایید پرداخت ناموفق بود'
        }
    
    def _get_callback_url(self):
        """Get callback URL for Pay.ir."""
        return f"{settings.SITE_URL.rstrip('/')}/payments/callback/payir/"


class NextpayGateway(PaymentGatewayBase):
    """NextPay payment gateway integration."""
    
    GATEWAY_NAME = 'nextpay'
    SANDBOX_URL = 'https://nextpay.ir/nx/gateway/token'
    PRODUCTION_URL = 'https://nextpay.ir/nx/gateway/token'
    VERIFY_URL = 'https://nextpay.ir/nx/gateway/verify'
    
    def __init__(self, gateway):
        super().__init__(gateway)
        self.api_key = self.config.get('API_KEY', '')
        self.sandbox = self.config.get('SANDBOX', True)
    
    def get_redirect_url(self, transaction):
        """Generate NextPay payment URL."""
        callback_url = self._get_callback_url()
        
        data = {
            'api_key': self.api_key,
            'amount': int(transaction.amount),
            'order_id': str(transaction.transaction_id),
            'callback_uri': callback_url,
            'customer_id': str(transaction.user.id) if transaction.user else '',
            'custom_json_fields': json.dumps({
                'order_id': transaction.order.id if transaction.order else None
            }),
        }
        
        response = requests.post(self.SANDBOX_URL if self.sandbox else self.PRODUCTION_URL, 
                               json=data)
        
        result = response.json()
        
        if result.get('code') == -1:
            trans_id = result.get('trans_id')
            transaction.gateway_reference = trans_id
            transaction.save()
            return f'https://nextpay.ir/nx/gateway/payment/{trans_id}'
        else:
            error_code = result.get('code', -1)
            error_message = result.get('message', 'خطا در اتصال به درگاه')
            transaction.error_code = str(error_code)
            transaction.error_message = error_message
            transaction.status = 'failed'
            transaction.save()
            return None
    
    def verify_payment(self, request_data):
        """Verify NextPay payment."""
        trans_id = request_data.get('trans_id')
        order_id = request_data.get('order_id')
        
        transaction = Transaction.objects.filter(
            transaction_id=order_id,
            gateway=self.gateway,
            status='pending'
        ).first()
        
        if not transaction:
            return None, {'success': False, 'message': 'تراکنش یافت نشد'}
        
        data = {
            'api_key': self.api_key,
            'trans_id': trans_id,
            'amount': int(transaction.amount),
        }
        
        response = requests.post(self.VERIFY_URL, json=data)
        
        result = response.json()
        
        if result.get('code') == 0:
            transaction.gateway_reference = trans_id
            transaction.gateway_response = result
            transaction.status = 'success'
            transaction.completed_at = timezone.now()
            transaction.save()
            
            return transaction, {
                'success': True,
                'message': 'پرداخت با موفقیت تایید شد'
            }
        else:
            error_code = result.get('code', -1)
            error_message = result.get('message', 'تایید پرداخت ناموفق بود')
            transaction.error_code = str(error_code)
            transaction.error_message = error_message
            transaction.status = 'failed'
            transaction.save()
            
            return transaction, {
                'success': False,
                'message': error_message
            }
    
    def _get_callback_url(self):
        """Get callback URL for NextPay."""
        return f"{settings.SITE_URL.rstrip('/')}/payments/callback/nextpay/"


class PaymentService:
    """Main payment service to handle all gateways."""
    
    GATEWAY_CLASSES = {
        'zarinpal': ZarinpalGateway,
        'idpay': IDPayGateway,
        'payir': PayIRGateway,
        'nextpay': NextpayGateway,
    }
    
    @classmethod
    def get_gateway(cls, gateway_type):
        """Get gateway instance by type."""
        gateway = PaymentGateway.objects.filter(
            gateway_type=gateway_type,
            is_active=True
        ).first()
        
        if not gateway:
            return None
        
        gateway_class = cls.GATEWAY_CLASSES.get(gateway_type)
        if gateway_class:
            return gateway_class(gateway)
        return None
    
    @classmethod
    def get_active_gateways(cls):
        """Get list of active gateways."""
        return PaymentGateway.objects.filter(is_active=True).order_by('sort_order')
    
    @classmethod
    def create_payment(cls, order, user, gateway_type, amount=None, **kwargs):
        """Create a payment transaction."""
        gateway = cls.get_gateway(gateway_type)
        if not gateway:
            return None, {'success': False, 'message': 'درگاه پرداخت یافت نشد'}
        
        amount = amount or order.total_amount
        
        transaction = gateway.create_transaction(
            order=order,
            user=user,
            amount=amount,
            **kwargs
        )
        
        return transaction, {'success': True, 'transaction': transaction}
    
    @classmethod
    def process_payment(cls, transaction, gateway_type):
        """Process payment and get redirect URL."""
        gateway = cls.get_gateway(gateway_type)
        if not gateway:
            return None, {'success': False, 'message': 'درگاه پرداخت یافت نشد'}
        
        redirect_url = gateway.get_redirect_url(transaction)
        
        if redirect_url:
            return redirect_url, {'success': True, 'url': redirect_url}
        else:
            return None, {'success': False, 'message': transaction.error_message or 'خطا در ایجاد لینک پرداخت'}
    
    @classmethod
    def verify_payment(cls, gateway_type, request_data):
        """Verify payment from callback."""
        gateway = cls.get_gateway(gateway_type)
        if not gateway:
            return None, {'success': False, 'message': 'درگاه پرداخت یافت نشد'}
        
        return gateway.verify_payment(request_data)
    
    @classmethod
    def get_callback_url(cls, gateway_type):
        """Get callback URL for a gateway."""
        gateway = cls.get_gateway(gateway_type)
        if gateway:
            return gateway._get_callback_url()
        return None
