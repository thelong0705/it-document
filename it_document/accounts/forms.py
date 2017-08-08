from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(max_length=200)

    class Meta:
        fields = ['username', 'email', 'password1', 'password2']
        model = User


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

