from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model  = CustomUser
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'phone', 'address',
            'password1', 'password2',
        )
