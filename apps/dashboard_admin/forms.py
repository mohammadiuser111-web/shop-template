"""
Forms for dashboard_admin app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    AdminDashboard,
    DashboardWidget,
    AdminMenu,
    AdminMenuItem,
    AdminQuickAction,
    AdminSettings,
    AdminUserSettings,
)


class AdminDashboardForm(forms.ModelForm):
    """Form for AdminDashboard model."""
    
    class Meta:
        model = AdminDashboard
        fields = '__all__'
        widgets = {
            'layout': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'JSON configuration for dashboard layout'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'name': _('نام'),
            'code': _('کد'),
            'description': _('توضیحات'),
            'layout': _('تنظیمات Layout'),
            'is_default': _('پیش‌فرض'),
            'is_active': _('فعال'),
        }


class DashboardWidgetForm(forms.ModelForm):
    """Form for DashboardWidget model."""
    
    class Meta:
        model = DashboardWidget
        fields = '__all__'
        widgets = {
            'config': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'JSON configuration for widget'
            }),
        }
        labels = {
            'name': _('نام'),
            'code': _('کد'),
            'widget_type': _('نوع ویجت'),
            'chart_type': _('نوع چارت'),
            'config': _('تنظیمات'),
            'title': _('عنوان'),
            'icon': _('آیکون'),
            'color': _('رنگ'),
            'width': _('عرض'),
            'height': _('ارتفاع'),
            'sort_order': _('ترتیب'),
            'is_active': _('فعال'),
        }


class AdminMenuForm(forms.ModelForm):
    """Form for AdminMenu model."""
    
    class Meta:
        model = AdminMenu
        fields = '__all__'
        widgets = {
            'items': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'JSON array of menu items'
            }),
        }
        labels = {
            'name': _('نام'),
            'menu_type': _('نوع منو'),
            'items': _('آیتم‌های منو'),
            'sort_order': _('ترتیب'),
            'is_active': _('فعال'),
        }


class AdminMenuItemForm(forms.ModelForm):
    """Form for AdminMenuItem model."""
    
    class Meta:
        model = AdminMenuItem
        fields = '__all__'
        labels = {
            'menu': _('منو'),
            'parent': _('والد'),
            'item_type': _('نوع آیتم'),
            'title': _('عنوان'),
            'icon': _('آیکون'),
            'color': _('رنگ'),
            'url': _('آدرس'),
            'target': _('هدف'),
            'required_permission': _('دسترسی مورد نیاز'),
            'sort_order': _('ترتیب'),
            'is_visible': _('قابل مشاهده'),
        }


class AdminQuickActionForm(forms.ModelForm):
    """Form for AdminQuickAction model."""
    
    class Meta:
        model = AdminQuickAction
        fields = '__all__'
        widgets = {
            'action_config': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'JSON configuration for action'
            }),
        }
        labels = {
            'name': _('نام'),
            'code': _('کد'),
            'action_type': _('نوع عمل'),
            'action_config': _('تنظیمات عمل'),
            'title': _('عنوان'),
            'icon': _('آیکون'),
            'color': _('رنگ'),
            'required_permission': _('دسترسی مورد نیاز'),
            'sort_order': _('ترتیب'),
            'is_active': _('فعال'),
        }


class AdminSettingsForm(forms.ModelForm):
    """Form for AdminSettings model."""
    
    class Meta:
        model = AdminSettings
        fields = '__all__'
        widgets = {
            'theme_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color'
            }),
            'sidebar_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color'
            }),
            'sidebar_text_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color'
            }),
        }
        labels = {
            'logo': _('لوگو'),
            'logo_small': _('لوگو کوچک'),
            'favicon': _('فاوآیکون'),
            'theme_color': _('رنگ تم'),
            'sidebar_color': _('رنگ سایدبار'),
            'sidebar_text_color': _('رنگ متن سایدبار'),
            'sidebar_collapsed': _('سایدبار جمع شده'),
            'layout': _('لایوت'),
            'language': _('زبان'),
            'show_notifications': _('نمایش اعلان‌ها'),
            'default_dashboard': _('داشبورد پیش‌فرض'),
        }


class AdminUserSettingsForm(forms.ModelForm):
    """Form for AdminUserSettings model."""
    
    class Meta:
        model = AdminUserSettings
        fields = '__all__'
        labels = {
            'user': _('کاربر'),
            'theme': _('تم'),
            'language': _('زبان'),
            'sidebar_collapsed': _('سایدبار جمع شده'),
            'email_notifications': _('اعلان‌های ایمیل'),
            'push_notifications': _('اعلان‌های پوش'),
            'dashboard': _('داشبورد'),
        }


class DashboardSettingsForm(forms.Form):
    """Form for user dashboard settings."""
    
    THEME_CHOICES = [
        ('light', _('روشن')),
        ('dark', _('تیره')),
        ('auto', _('اتوماتیک')),
    ]
    
    LANGUAGE_CHOICES = [
        ('fa', _('فارسی')),
        ('en', _('انگلیسی')),
    ]
    
    theme = forms.ChoiceField(
        choices=THEME_CHOICES,
        label=_('تم'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        label=_('زبان'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sidebar_collapsed = forms.BooleanField(
        label=_('سایدبار جمع شده'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    email_notifications = forms.BooleanField(
        label=_('اعلان‌های ایمیل'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    push_notifications = forms.BooleanField(
        label=_('اعلان‌های پوش'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class WidgetConfigForm(forms.Form):
    """Form for widget configuration."""
    
    WIDGET_TYPE_CHOICES = [
        ('chart', _('چارت')),
        ('statistic', _('آمار')),
        ('list', _('لیست')),
        ('card', _('کارت')),
    ]
    
    CHART_TYPE_CHOICES = [
        ('line', _('خطی')),
        ('bar', _('میله‌ای')),
        ('pie', _('دایره‌ای')),
        ('doughnut', _('دانات')),
        ('polar', _('قطبی')),
        ('radar', _('رادار')),
    ]
    
    widget_type = forms.ChoiceField(
        choices=WIDGET_TYPE_CHOICES,
        label=_('نوع ویجت'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    chart_type = forms.ChoiceField(
        choices=CHART_TYPE_CHOICES,
        label=_('نوع چارت'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    title = forms.CharField(
        label=_('عنوان'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    icon = forms.CharField(
        label=_('آیکون'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    color = forms.CharField(
        label=_('رنگ'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control color-picker', 'type': 'color'})
    )
    
    width = forms.ChoiceField(
        choices=[
            ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('6', '6'), ('12', '12')
        ],
        label=_('عرض'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    height = forms.ChoiceField(
        choices=[
            ('auto', 'اتوماتیک'), ('100', '100px'), ('200', '200px'), ('300', '300px')
        ],
        label=_('ارتفاع'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    data_source = forms.ChoiceField(
        choices=[
            ('sales_by_day', _('فروش بر اساس روز')),
            ('sales_by_category', _('فروش بر اساس دسته')),
            ('orders_by_status', _('سفارشات بر اساس وضعیت')),
            ('custom', _('سفارشی')),
        ],
        label=_('منبع داده'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
