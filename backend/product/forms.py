from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Product
        fields = ('title', 'description', 'category')
