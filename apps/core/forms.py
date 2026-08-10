"""
Forms for core app.
"""
from django import forms
from django.conf import settings
from .models import ThemeConfig, SiteSettings
import json


class ThemeConfigForm(forms.ModelForm):
    """Form for theme configuration."""
    
    class Meta:
        model = ThemeConfig
        fields = ['name', 'config_json', 'is_active']
        widgets = {
            'config_json': forms.Textarea(attrs={
                'class': 'form-control code-editor',
                'rows': 20,
                'placeholder': 'Enter JSON configuration',
            }),
        }
    
    def clean_config_json(self):
        """Validate JSON configuration."""
        config_json = self.cleaned_data.get('config_json')
        try:
            json.loads(config_json)
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Invalid JSON: {e}")
        return config_json


class SiteSettingsForm(forms.ModelForm):
    """Form for site settings."""
    
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'site_description', 'site_logo', 'site_favicon',
            'contact_email', 'contact_phone', 'address',
            'facebook_url', 'twitter_url', 'instagram_url', 'telegram_url', 'linkedin_url',
            'currency', 'currency_symbol', 'default_tax_rate',
            'meta_title', 'meta_description', 'meta_keywords',
            'maintenance_mode', 'maintenance_message',
        ]
        widgets = {
            'site_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta_keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'maintenance_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ContactForm(forms.Form):
    """Form for contact us page."""
    
    name = forms.CharField(
        label='نام و نام خانوادگی',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام و نام خانوادگی'})
    )
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'})
    )
    phone = forms.CharField(
        label='شماره تلفن',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09123456789'})
    )
    subject = forms.CharField(
        label='موضوع',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع پیام'})
    )
    message = forms.CharField(
        label='پیام',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'متن پیام'})
    )
    
    def clean_phone(self):
        """Clean and validate phone number."""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters
            phone = ''.join(c for c in phone if c.isdigit())
            if len(phone) < 10:
                raise forms.ValidationError('شماره تلفن باید حداقل 10 رقم باشد')
        return phone


class SearchForm(forms.Form):
    """Form for search."""
    
    q = forms.CharField(
        label='جستجو',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control search-input',
            'placeholder': 'جستجوی محصولات...',
        })
    )
    category = forms.CharField(
        label='دسته‌بندی',
        required=False,
        widget=forms.HiddenInput()
    )
    brand = forms.CharField(
        label='برند',
        required=False,
        widget=forms.HiddenInput()
    )
    min_price = forms.DecimalField(
        label='قیمت حداقل',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    max_price = forms.DecimalField(
        label='قیمت حداکثر',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    in_stock = forms.BooleanField(
        label='موجود در انبار',
        required=False,
        widget=forms.CheckboxInput()
    )
    on_sale = forms.BooleanField(
        label='تخفیف',
        required=False,
        widget=forms.CheckboxInput()
    )
    sort_by = forms.ChoiceField(
        label='مرتب‌سازی',
        choices=[
            ('newest', 'جدیدترین'),
            ('price_low', 'ارزان‌ترین'),
            ('price_high', 'گران‌ترین'),
            ('rating', 'بیشترین امتیاز'),
            ('popular', 'محبوب‌ترین'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
