"""
Forms for cart app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _


class AddToCartForm(forms.Form):
    """Form for adding items to cart."""
    
    product_id = forms.UUIDField(widget=forms.HiddenInput())
    variant_id = forms.UUIDField(required=False, widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        label=_('Quantity'),
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'min': '1',
        })
    )
    
    def clean_quantity(self):
        """Validate quantity."""
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError(_('Quantity must be at least 1'))
        return quantity


class UpdateCartItemForm(forms.Form):
    """Form for updating cart item quantity."""
    
    item_id = forms.UUIDField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        label=_('Quantity'),
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'min': '1',
        })
    )
    
    def clean_quantity(self):
        """Validate quantity."""
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError(_('Quantity must be at least 1'))
        return quantity


class RemoveFromCartForm(forms.Form):
    """Form for removing item from cart."""
    
    item_id = forms.UUIDField(widget=forms.HiddenInput())


class ClearCartForm(forms.Form):
    """Form for clearing cart."""
    
    confirm = forms.BooleanField(
        label=_('Are you sure you want to clear your cart?'),
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class ApplyCouponForm(forms.Form):
    """Form for applying coupon to cart."""
    
    coupon_code = forms.CharField(
        label=_('Coupon Code'),
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد تخفیف',
        })
    )


class RemoveCouponForm(forms.Form):
    """Form for removing coupon from cart."""
    
    confirm = forms.BooleanField(
        label=_('Remove coupon?'),
        required=True,
        widget=forms.HiddenInput()
    )
