"""
Forms for blog app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Article, Comment, BlogCategory, Tag


class ArticleForm(forms.ModelForm):
    """Form for creating and updating articles."""
    
    categories = forms.ModelMultipleChoiceField(
        queryset=BlogCategory.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Categories')
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Tags')
    )
    
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'excerpt', 'content', 'author',
            'featured_image', 'featured_image_caption',
            'status', 'is_featured', 'is_popular', 'allow_comments',
            'published_at', 'scheduled_at',
            'meta_title', 'meta_description', 'meta_keywords', 'canonical_url',
        ]
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 20}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug and Article.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('An article with this slug already exists.'))
        return slug


class CommentForm(forms.ModelForm):
    """Form for submitting comments."""
    
    class Meta:
        model = Comment
        fields = ['author_name', 'author_email', 'author_website', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
    def clean_author_email(self):
        email = self.cleaned_data.get('author_email')
        if email and Comment.objects.filter(
            author_email=email,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).exists():
            raise ValidationError(_('You have already submitted a comment recently. Please wait before submitting another.'))
        return email
