from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email','address', 'phone_number', 'password1','password2')
        labels = {
            'email': 'メールアドレス',
            'address': '住所',
            'phone_number': '電話番号',
            'password1': 'パスワード',
            'password2': 'パスワードの確認',
        }