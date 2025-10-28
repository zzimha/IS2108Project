from django import forms
from storefront.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'category',
            'price',
            'stock',
            'reorder_threshold',
            'rating',
            'is_on_sale',
            'original_price',
            'discount_percentage',
            'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


