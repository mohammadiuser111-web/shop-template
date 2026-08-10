"""
Forms for orders app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order


class CheckoutForm(forms.Form):
    """Form for checkout process."""
    
    # Step 1: Address Information
    first_name = forms.CharField(
        label=_('First Name'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        label=_('Phone Number'),
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Shipping Address
    shipping_address_line_1 = forms.CharField(
        label=_('Shipping Address Line 1'),
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_address_line_2 = forms.CharField(
        label=_('Shipping Address Line 2'),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_city = forms.CharField(
        label=_('City'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_state = forms.CharField(
        label=_('State'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_postal_code = forms.CharField(
        label=_('Postal Code'),
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_country = forms.CharField(
        label=_('Country'),
        max_length=100,
        initial='Iran',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Billing Address (same as shipping by default)
    same_as_shipping = forms.BooleanField(
        label=_('Billing address same as shipping'),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    billing_address_line_1 = forms.CharField(
        label=_('Billing Address Line 1'),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    billing_address_line_2 = forms.CharField(
        label=_('Billing Address Line 2'),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    billing_city = forms.CharField(
        label=_('City'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    billing_state = forms.CharField(
        label=_('State'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    billing_postal_code = forms.CharField(
        label=_('Postal Code'),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    billing_country = forms.CharField(
        label=_('Country'),
        max_length=100,
        required=False,
        initial='Iran',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Step 2: Shipping Method
    shipping_method = forms.CharField(
        label=_('Shipping Method'),
        widget=forms.HiddenInput()
    )
    
    # Step 3: Payment Method
    payment_method = forms.ChoiceField(
        label=_('Payment Method'),
        choices=Order.PAYMENT_METHODS,
        widget=forms.RadioSelect(attrs={'class': 'payment-method-select'})
    )
    
    # Additional fields
    customer_notes = forms.CharField(
        label=_('Order Notes'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'یادداشت‌های سفارش (اختیاری)',
        })
    )
    
    def clean(self):
        """Clean form data."""
        cleaned_data = super().clean()
        
        # If same as shipping, copy shipping address to billing
        if cleaned_data.get('same_as_shipping'):
            cleaned_data['billing_address_line_1'] = cleaned_data.get('shipping_address_line_1')
            cleaned_data['billing_address_line_2'] = cleaned_data.get('shipping_address_line_2')
            cleaned_data['billing_city'] = cleaned_data.get('shipping_city')
            cleaned_data['billing_state'] = cleaned_data.get('shipping_state')
            cleaned_data['billing_postal_code'] = cleaned_data.get('shipping_postal_code')
            cleaned_data['billing_country'] = cleaned_data.get('shipping_country')
        
        return cleaned_data


class OrderCancelForm(forms.Form):
    """Form for cancelling an order."""
    
    reason = forms.ChoiceField(
        label=_('Reason for Cancellation'),
        choices=[
            ('changed_mind', _('Changed my mind')),
            ('found_cheaper', _('Found a cheaper option')),
            ('shipping_delay', _('Shipping delay')),
            ('wrong_product', _('Ordered wrong product')),
            ('other', _('Other')),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        label=_('Additional Notes'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'توضیحات اضافی (اختیاری)',
        })
    )


class RefundRequestForm(forms.Form):
    """Form for requesting a refund."""
    
    order_item = forms.CharField(
        label=_('Order Item'),
        widget=forms.HiddenInput()
    )
    reason = forms.ChoiceField(
        label=_('Reason for Refund'),
        choices=[
            ('defective', _('Defective Product')),
            ('wrong_item', _('Wrong Item Shipped')),
            ('not_as_described', _('Not As Described')),
            ('changed_mind', _('Changed Mind')),
            ('other', _('Other')),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    reason_details = forms.CharField(
        label=_('Details'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'توضیحات بیشتر',
        })
    )


class OrderNoteForm(forms.Form):
    """Form for adding notes to an order."""
    
    notes = forms.CharField(
        label=_('Notes'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
        })
    )


class OrderStatusForm(forms.Form):
    """Form for updating order status."""
    
    status = forms.ChoiceField(
        label=_('Status'),
        choices=Order.ORDER_STATUS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        label=_('Notes'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
        })
    )
    tracking_number = forms.CharField(
        label=_('Tracking Number'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class BulkOrderUpdateForm(forms.Form):
    """Form for bulk order updates."""
    
    ACTION_CHOICES = [
        ('update_status', _('Update Status')),
        ('mark_paid', _('Mark as Paid')),
        ('mark_shipped', _('Mark as Shipped')),
        ('mark_delivered', _('Mark as Delivered')),
        ('mark_cancelled', _('Mark as Cancelled')),
    ]
    
    action = forms.ChoiceField(
        label=_('Action'),
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=Order.ORDER_STATUS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        label=_('Notes'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
        })
    )
