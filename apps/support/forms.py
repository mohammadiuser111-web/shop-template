"""
Forms for support app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Ticket, TicketMessage, FAQ, SupportCategory, TicketPriority


class TicketForm(forms.ModelForm):
    """Form for creating and updating tickets."""
    
    class Meta:
        model = Ticket
        fields = [
            'subject', 'content', 'category', 'priority',
            'customer_name', 'customer_email', 'customer_phone',
            'order', 'product',
        ]
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_authenticated:
            self.fields['customer_name'].initial = user.get_full_name() or user.username
            self.fields['customer_email'].initial = user.email
            self.fields['customer_phone'].initial = getattr(user, 'phone_number', '')
            self.fields['customer_name'].widget = forms.HiddenInput()
            self.fields['customer_email'].widget = forms.HiddenInput()
            self.fields['customer_phone'].widget = forms.HiddenInput()


class TicketMessageForm(forms.ModelForm):
    """Form for adding ticket messages."""
    
    class Meta:
        model = TicketMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class FAQForm(forms.ModelForm):
    """Form for creating and updating FAQs."""
    
    class Meta:
        model = FAQ
        fields = [
            'question', 'answer', 'category', 'tags',
            'slug', 'meta_title', 'meta_description',
            'is_active', 'is_featured', 'sort_order',
        ]
        widgets = {
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'question': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ContactForm(forms.Form):
    """Form for contact page."""
    
    DEPARTMENT_CHOICES = [
        ('sales', _('Sales')),
        ('support', _('Technical Support')),
        ('billing', _('Billing')),
        ('general', _('General Inquiry')),
    ]
    
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Your Name')
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label=_('Your Email')
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Your Phone')
    )
    subject = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Subject')
    )
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Department')
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
        label=_('Message')
    )


class TicketSearchForm(forms.Form):
    """Form for searching tickets."""
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Search by ticket number, subject, or description...')}),
        label=_('Search')
    )
    category = forms.ModelChoiceField(
        queryset=SupportCategory.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Category')
    )
    status = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Status')
    )
    priority = forms.ModelChoiceField(
        queryset=TicketPriority.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Priority')
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set status choices dynamically
        from .models import TicketStatus
        self.fields['status'].choices = [
            ('', _('All Statuses')),
            *[(s.code, s.name) for s in TicketStatus.objects.all()]
        ]
        
        # Filter categories based on user permissions
        if user and not user.is_staff:
            self.fields['category'].queryset = SupportCategory.objects.none()
