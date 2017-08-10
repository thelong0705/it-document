from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(max_length=200)

    class Meta:
        fields = ['username', 'email', 'password1', 'password2']
        model = User


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(required=False)
    email = forms.EmailField(required=False)


class ChangePasswordForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['password1', 'password2']
