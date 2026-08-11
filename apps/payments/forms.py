"""
Forms for payments app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PaymentGateway, Transaction, Wallet


class PaymentGatewayForm(forms.ModelForm):
    """Form for PaymentGateway model."""
    
    class Meta:
        model = PaymentGateway
        fields = '__all__'
        widgets = {
            'config': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'JSON configuration for gateway'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'name': _('نام'),
            'gateway_type': _('نوع درگاه'),
            'config': _('تنظیمات'),
            'title': _('عنوان'),
            'description': _('توضیحات'),
            'logo': _('لوگو'),
            'is_active': _('فعال'),
            'sort_order': _('ترتیب'),
        }


class TransactionForm(forms.ModelForm):
    """Form for Transaction model."""
    
    class Meta:
        model = Transaction
        fields = [
            'amount', 'currency', 'customer_name', 
            'customer_email', 'customer_phone'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'amount': _('مبلغ'),
            'currency': _('ارز'),
            'customer_name': _('نام مشتری'),
            'customer_email': _('ایمیل مشتری'),
            'customer_phone': _('تلفن مشتری'),
        }


class WalletDepositForm(forms.Form):
    """Form for wallet deposit."""
    
    amount = forms.DecimalField(
        label=_('مبلغ'),
        max_digits=12,
        decimal_places=2,
        min_value=1000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مبلغ به تومان'})
    )
    description = forms.CharField(
        label=_('توضیحات'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'توضیحات (اختیاری)'})
    )


class WalletWithdrawForm(forms.Form):
    """Form for wallet withdrawal."""
    
    amount = forms.DecimalField(
        label=_('مبلغ'),
        max_digits=12,
        decimal_places=2,
        min_value=1000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مبلغ به تومان'})
    )
    description = forms.CharField(
        label=_('توضیحات'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'توضیحات (اختیاری)'})
    )
    
    def clean_amount(self):
        """Check if user has sufficient balance."""
        amount = self.cleaned_data.get('amount')
        user = self.context.get('user')
        
        if user and hasattr(user, 'wallet'):
            wallet = user.wallet
            if wallet.balance < amount:
                raise forms.ValidationError(_('موجودی کافی نیست. موجودی فعلی: %(balance)s تومان') % {'balance': wallet.balance})
        
        return amount


class PaymentForm(forms.Form):
    """Form for payment processing."""
    
    GATEWAY_CHOICES = [
        ('zarinpal', _('زرین پال')),
        ('idpay', _('آی دی پی')),
        ('payir', _('پی آی آر')),
        ('nextpay', _('نکست پی')),
    ]
    
    gateway = forms.ChoiceField(
        choices=GATEWAY_CHOICES,
        label=_('درگاه پرداخت'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    amount = forms.DecimalField(
        label=_('مبلغ'),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    
    order_id = forms.UUIDField(
        label=_('شناسه سفارش'),
        widget=forms.HiddenInput()
    )
    
    description = forms.CharField(
        label=_('توضیحات'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class RefundForm(forms.Form):
    """Form for refund requests."""
    
    transaction_id = forms.UUIDField(
        label=_('شناسه تراکنش'),
        widget=forms.HiddenInput()
    )
    
    amount = forms.DecimalField(
        label=_('مبلغ استرداد'),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    reason = forms.CharField(
        label=_('دلیل استرداد'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class PaymentSearchForm(forms.Form):
    """Form for searching payments."""
    
    transaction_id = forms.CharField(
        label=_('شناسه تراکنش'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شناسه تراکنش'})
    )
    
    gateway = forms.CharField(
        label=_('درگاه'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        label=_('وضعیت'),
        required=False,
        choices=[
            ('', _('همه')),
            ('pending', _('در انتظار')),
            ('success', _('موفق')),
            ('failed', _('ناموفق')),
            ('cancelled', _('لغو شده')),
            ('refunded', _('استرداد شده')),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        label=_('از تاریخ'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_to = forms.DateField(
        label=_('تا تاریخ'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
