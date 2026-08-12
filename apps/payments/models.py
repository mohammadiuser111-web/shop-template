"""
Payment models for shop-template project.
"""
from django.db import models
from django.conf import settings
import uuid


class PaymentGateway(models.Model):
    """
    Model for payment gateways configuration.
    """
    GATEWAY_TYPES = [
        ('zarinpal', 'Zarinpal'),
        ('idpay', 'IDPay'),
        ('payir', 'Pay.ir'),
        ('nextpay', 'NextPay'),
        ('custom', 'Custom Gateway'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Name')
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES, verbose_name='Gateway Type')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    # Configuration
    config = models.JSONField(verbose_name='Configuration', default=dict)
    
    # Display settings
    title = models.CharField(max_length=100, verbose_name='Display Title')
    description = models.TextField(verbose_name='Description', blank=True)
    logo = models.ImageField(upload_to='payment_gateways/', verbose_name='Logo', null=True, blank=True)
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.title
    
    def get_config_value(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)


class Transaction(models.Model):
    """
    Model for payment transactions.
    """
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('refund', 'Refund'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=200, unique=True, verbose_name='Transaction ID')
    
    # Related objects
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='transactions',
        null=True,
        blank=True,
        verbose_name='User'
    )
    
    # Transaction details
    gateway = models.ForeignKey(
        PaymentGateway,
        on_delete=models.SET_NULL,
        related_name='transactions',
        null=True,
        blank=True,
        verbose_name='Payment Gateway'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='purchase',
                                        verbose_name='Transaction Type')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Amount')
    currency = models.CharField(max_length=3, default='IRR', verbose_name='Currency')
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending',
                              verbose_name='Status')
    
    # Gateway response
    gateway_reference = models.CharField(max_length=200, verbose_name='Gateway Reference', blank=True)
    gateway_response = models.JSONField(verbose_name='Gateway Response', default=dict, blank=True)
    
    # User information
    customer_name = models.CharField(max_length=200, verbose_name='Customer Name', blank=True)
    customer_email = models.EmailField(verbose_name='Customer Email', blank=True)
    customer_phone = models.CharField(max_length=20, verbose_name='Customer Phone', blank=True)
    
    # Error information
    error_code = models.CharField(max_length=50, verbose_name='Error Code', blank=True)
    error_message = models.TextField(verbose_name='Error Message', blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    completed_at = models.DateTimeField(verbose_name='Completed At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['user']),
            models.Index(fields=['gateway']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"Transaction #{self.transaction_id}"
    
    def mark_as_success(self, gateway_reference=None, gateway_response=None):
        """Mark transaction as successful."""
        self.status = 'success'
        self.completed_at = models.DateTimeField(auto_now_add=True)
        if gateway_reference:
            self.gateway_reference = gateway_reference
        if gateway_response:
            self.gateway_response = gateway_response
        self.save()
    
    def mark_as_failed(self, error_code=None, error_message=None):
        """Mark transaction as failed."""
        self.status = 'failed'
        if error_code:
            self.error_code = error_code
        if error_message:
            self.error_message = error_message
        self.save()
    
    def mark_as_cancelled(self):
        """Mark transaction as cancelled."""
        self.status = 'cancelled'
        self.save()


class Wallet(models.Model):
    """
    Model for user wallet.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name='User'
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Balance')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
    
    def __str__(self):
        return f"Wallet - {self.user}"
    
    def add_balance(self, amount, description=None):
        """Add balance to wallet."""
        from django.utils import timezone
        self.balance += amount
        self.save()
        
        WalletTransaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type='deposit',
            balance_after=self.balance,
            description=description or f'Add {amount} to wallet'
        )
    
    def subtract_balance(self, amount, description=None):
        """Subtract balance from wallet."""
        from django.utils import timezone
        if self.balance < amount:
            raise ValueError('Insufficient balance')
        
        self.balance -= amount
        self.save()
        
        WalletTransaction.objects.create(
            wallet=self,
            amount=-amount,
            transaction_type='withdrawal',
            balance_after=self.balance,
            description=description or f'Subtract {amount} from wallet'
        )


class WalletTransaction(models.Model):
    """
    Model for wallet transactions.
    """
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('refund', 'Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Wallet'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Amount')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='Transaction Type')
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Balance After')
    description = models.TextField(verbose_name='Description', blank=True)
    
    # Related transaction
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        related_name='wallet_transactions',
        null=True,
        blank=True,
        verbose_name='Transaction'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount}"
