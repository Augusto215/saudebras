# forms.py

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAuthForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail não está registrado.")
        
        user = User.objects.get(email=email)
        
        if not user.check_password(password):
            raise forms.ValidationError("Senha incorreta.")
