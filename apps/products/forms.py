"""
Forms for products app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    Category, Brand, Attribute, AttributeValue, 
    Product, ProductImage, ProductVariant, Tag
)


class CategoryForm(forms.ModelForm):
    """Form for category."""
    
    class Meta:
        model = Category
        fields = [
            'name', 'slug', 'description', 'parent', 
            'image', 'icon', 'is_active', 'sort_order',
            'meta_title', 'meta_description', 'meta_keywords',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta_keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_slug(self):
        """Clean slug."""
        slug = self.cleaned_data.get('slug')
        if slug:
            slug = slug.lower().replace(' ', '-')
        return slug


class BrandForm(forms.ModelForm):
    """Form for brand."""
    
    class Meta:
        model = Brand
        fields = [
            'name', 'slug', 'description', 'logo',
            'website', 'country', 'is_active', 'sort_order',
            'meta_title', 'meta_description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AttributeForm(forms.ModelForm):
    """Form for attribute."""
    
    class Meta:
        model = Attribute
        fields = [
            'name', 'slug', 'attribute_type', 'description',
            'is_filterable', 'is_required', 'is_variant',
            'sort_order', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'attribute_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_filterable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_variant': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AttributeValueForm(forms.ModelForm):
    """Form for attribute value."""
    
    class Meta:
        model = AttributeValue
        fields = ['attribute', 'value', 'color_code', 'sort_order', 'is_active']
        widgets = {
            'attribute': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
            'color_code': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color',
            }),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductForm(forms.ModelForm):
    """Form for product."""
    
    class Meta:
        model = Product
        fields = [
            'sku', 'name', 'slug', 'product_type',
            'category', 'brand',
            'short_description', 'description', 'specifications',
            'regular_price', 'sale_price', 'cost_price',
            'stock_quantity', 'stock_status', 'low_stock_threshold', 'allow_backorders',
            'weight', 'length', 'width', 'height',
            'featured_image',
            'is_active', 'is_featured', 'is_best_seller', 'is_new', 'is_on_sale',
            'published_at',
            'meta_title', 'meta_description', 'meta_keywords',
            'related_products', 'upsell_products', 'cross_sell_products',
            'tags',
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'regular_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_status': forms.Select(attrs={'class': 'form-control'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control'}),
            'allow_backorders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_best_seller': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_on_sale': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'published_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta_keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'related_products': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'upsell_products': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'cross_sell_products': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class ProductImageForm(forms.ModelForm):
    """Form for product image."""
    
    class Meta:
        model = ProductImage
        fields = ['product', 'image', 'alt_text', 'sort_order', 'is_featured']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductVariantForm(forms.ModelForm):
    """Form for product variant."""
    
    class Meta:
        model = ProductVariant
        fields = [
            'product', 'sku', 'name',
            'attribute_values',
            'regular_price', 'sale_price',
            'stock_quantity', 'stock_status',
            'weight',
            'image',
            'is_active',
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'attribute_values': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'regular_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_status': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TagForm(forms.ModelForm):
    """Form for tag."""
    
    class Meta:
        model = Tag
        fields = ['name', 'slug', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color',
            }),
        }


class ProductSearchForm(forms.Form):
    """Form for product search and filtering."""
    
    q = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'جستجوی محصولات...',
        })
    )
    category = forms.ModelChoiceField(
        label=_('Category'),
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    brand = forms.ModelChoiceField(
        label=_('Brand'),
        queryset=Brand.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        label=_('Min Price'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    max_price = forms.DecimalField(
        label=_('Max Price'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    in_stock = forms.BooleanField(
        label=_('In Stock'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    on_sale = forms.BooleanField(
        label=_('On Sale'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    sort_by = forms.ChoiceField(
        label=_('Sort By'),
        choices=[
            ('newest', _('Newest')),
            ('price_low', _('Price: Low to High')),
            ('price_high', _('Price: High to Low')),
            ('rating', _('Rating')),
            ('popular', _('Popular')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tags = forms.ModelMultipleChoiceField(
        label=_('Tags'),
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )


class QuickAddToCartForm(forms.Form):
    """Form for quick add to cart."""
    
    product_id = forms.UUIDField(widget=forms.HiddenInput())
    variant_id = forms.UUIDField(required=False, widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        label=_('Quantity'),
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
