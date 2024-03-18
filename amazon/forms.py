from django import forms

from accounts.models import CustomUser
from .models import Product, Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = { 
            'rating': '評価',
            'comment': 'コメント'
        }

class AddressUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['address']
        labels = {
            'address': '新しい住所',  # ラベルを設定
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'brand', 'category', 'price', 'description', 'product_image']
        labels = {
            'product_name': '商品名',
            'brand': 'ブランド',
            'category': 'カテゴリ',
            'price': '価格',
            'description': '商品説明',
            'product_image': '商品画像',
        }