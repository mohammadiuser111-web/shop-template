"""
Forms for accounts app.
"""
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, UserAddress, OTP
import re

UserModel = get_user_model()


class LoginForm(AuthenticationForm):
    """Custom login form with phone/email support."""
    
    username = forms.CharField(
        label=_('Phone Number or Email'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'شماره تلفن یا ایمیل',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور',
        })
    )
    
    def clean_username(self):
        """Allow login with phone number or email."""
        username = self.cleaned_data.get('username')
        
        # Check if it's an email
        if '@' in username:
            try:
                user = UserModel.objects.get(email=username)
                return user.phone_number or user.email
            except UserModel.DoesNotExist:
                return username
        
        # Check if it's a phone number
        phone_regex = re.compile(r'^\+?1?\d{9,15}$')
        if phone_regex.match(username):
            return username
        
        return username


class RegistrationForm(forms.ModelForm):
    """Form for user registration."""
    
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور',
        })
    )
    password_confirm = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'تکرار رمز عبور',
        })
    )
    
    class Meta:
        model = UserModel
        fields = ['phone_number', 'email', 'first_name', 'last_name']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره تلفن (اختیاری)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ایمیل',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام خانوادگی',
            }),
        }
    
    def clean_password_confirm(self):
        """Check that passwords match."""
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError(_('Passwords do not match'))
        
        return password_confirm
    
    def clean_phone_number(self):
        """Clean and validate phone number."""
        phone_number = self.cleaned_data.get('phone_number')
        
        if phone_number:
            # Remove all non-digit characters except +
            phone_number = re.sub(r'[^\d+]', '', phone_number)
            
            # Validate phone number format
            phone_regex = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_regex.match(phone_number):
                raise ValidationError(_('Enter a valid phone number'))
        
        return phone_number
    
    def save(self, commit=True):
        """Save user with hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = True
        
        if commit:
            user.save()
        
        return user


class OTPLoginForm(forms.Form):
    """Form for OTP login."""
    
    phone_number = forms.CharField(
        label=_('Phone Number'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'شماره تلفن',
        })
    )
    
    def clean_phone_number(self):
        """Clean and validate phone number."""
        phone_number = self.cleaned_data.get('phone_number')
        
        # Remove all non-digit characters except +
        phone_number = re.sub(r'[^\d+]', '', phone_number)
        
        # Validate phone number format
        phone_regex = re.compile(r'^\+?1?\d{9,15}$')
        if not phone_regex.match(phone_number):
            raise ValidationError(_('Enter a valid phone number'))
        
        return phone_number


class OTPVerifyForm(forms.Form):
    """Form for OTP verification."""
    
    code = forms.CharField(
        label=_('Verification Code'),
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد تایید 6 رقمی',
            'autocomplete': 'off',
        })
    )
    
    def clean_code(self):
        """Clean and validate OTP code."""
        code = self.cleaned_data.get('code')
        
        # Remove all non-digit characters
        code = re.sub(r'\D', '', code)
        
        if len(code) != 6:
            raise ValidationError(_('Verification code must be 6 digits'))
        
        return code


class ProfileForm(forms.ModelForm):
    """Form for user profile."""
    
    class Meta:
        model = UserModel
        fields = [
            'first_name', 'last_name', 'phone_number', 'email',
            'gender', 'date_of_birth', 'avatar',
            'address', 'city', 'state', 'postal_code', 'country',
            'facebook_url', 'twitter_url', 'instagram_url',
            'newsletter_subscribed', 'preferred_language',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'newsletter_subscribed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preferred_language': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_phone_number(self):
        """Clean phone number."""
        phone_number = self.cleaned_data.get('phone_number')
        
        if phone_number:
            phone_number = re.sub(r'[^\d+]', '', phone_number)
        
        return phone_number


class UserAddressForm(forms.ModelForm):
    """Form for user address."""
    
    class Meta:
        model = UserAddress
        fields = [
            'address_type', 'recipient_name', 'phone_number',
            'address_line_1', 'address_line_2',
            'city', 'state', 'postal_code', 'country',
            'is_default', 'notes',
        ]
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PasswordChangeCustomForm(PasswordChangeForm):
    """Custom password change form."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})


class PasswordResetCustomForm(PasswordResetForm):
    """Custom password reset form."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'ایمیل',
        })


class SetPasswordCustomForm(SetPasswordForm):
    """Custom set password form."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
