"""
Forms for ads app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import AdSlot, Advertisement


class AdSlotForm(forms.ModelForm):
    """Form for AdSlot model."""
    
    class Meta:
        model = AdSlot
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('توضیحات slot')
            }),
        }
        labels = {
            'name': _('نام'),
            'code': _('کد'),
            'description': _('توضیحات'),
            'width': _('عرض (پیکسل)'),
            'height': _('ارتفاع (پیکسل)'),
            'is_responsive': _('واکنشگرا'),
            'is_active': _('فعال'),
        }


class AdvertisementForm(forms.ModelForm):
    """Form for Advertisement model."""
    
    class Meta:
        model = Advertisement
        fields = [
            'name', 'slot', 'ad_type', 'image', 'image_alt',
            'html_content', 'script_content', 'video_url', 'video_embed_code',
            'url', 'target', 'title', 'description', 'priority',
            'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('توضیحات تبلیغ')
            }),
            'html_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('کد HTML')
            }),
            'script_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('کد JavaScript')
            }),
            'video_embed_code': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('کد embed ویدئو')
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
        labels = {
            'name': _('نام'),
            'slot': _('Slot'),
            'ad_type': _('نوع تبلیغ'),
            'image': _('تصویر'),
            'image_alt': _('متن جایگزین تصویر'),
            'html_content': _('محتوا HTML'),
            'script_content': _('کد JavaScript'),
            'video_url': _('آدرس ویدئو'),
            'video_embed_code': _('کد embed ویدئو'),
            'url': _('آدرس لینک'),
            'target': _('مقال لینک'),
            'title': _('عنوان'),
            'description': _('توضیحات'),
            'priority': _('اولویت'),
            'start_date': _('تاریخ شروع'),
            'end_date': _('تاریخ پایان'),
            'is_active': _('فعال'),
        }
    
    def clean(self):
        """Validate ad content based on ad type."""
        cleaned_data = super().clean()
        ad_type = cleaned_data.get('ad_type')
        
        if ad_type == 'image':
            if not cleaned_data.get('image'):
                raise forms.ValidationError(
                    {'image': _('برای تبلیغات تصویری، انتخاب تصویر الزامی است.')}
                )
        elif ad_type == 'html':
            if not cleaned_data.get('html_content'):
                raise forms.ValidationError(
                    {'html_content': _('برای تبلیغات HTML، وارد کردن کد الزامی است.')}
                )
        elif ad_type == 'script':
            if not cleaned_data.get('script_content'):
                raise forms.ValidationError(
                    {'script_content': _('برای تبلیغات JavaScript، وارد کردن کد الزامی است.')}
                )
        elif ad_type == 'video':
            if not cleaned_data.get('video_url') and not cleaned_data.get('video_embed_code'):
                raise forms.ValidationError(
                    _('برای تبلیغات ویدئویی، وارد کردن آدرس یا کد embed الزامی است.')
                )
        
        return cleaned_data


class AdSearchForm(forms.Form):
    """Form for searching ads."""
    
    query = forms.CharField(
        label=_('جستجو'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('نام، کد، یا توضیحات')
        })
    )
    
    slot = forms.ModelChoiceField(
        label=_('Slot'),
        required=False,
        queryset=AdSlot.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    ad_type = forms.ChoiceField(
        label=_('نوع تبلیغ'),
        required=False,
        choices=[
            ('', _('همه')),
            ('image', _('تصویر')),
            ('html', _('HTML')),
            ('script', _('JavaScript')),
            ('video', _('ویدئو')),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.ChoiceField(
        label=_('وضعیت'),
        required=False,
        choices=[
            ('', _('همه')),
            ('1', _('فعال')),
            ('0', _('غیرفعال')),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class AdStatsForm(forms.Form):
    """Form for ad statistics filter."""
    
    date_from = forms.DateField(
        label=_('از تاریخ'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label=_('تا تاریخ'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    slot = forms.ModelChoiceField(
        label=_('Slot'),
        required=False,
        queryset=AdSlot.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class AdSlotFormSimple(forms.ModelForm):
    """Simplified form for quick ad slot creation."""
    
    class Meta:
        model = AdSlot
        fields = ['name', 'code', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': _('نام'),
            'code': _('کد'),
            'is_active': _('فعال'),
        }
