from django import forms
from .models import SystemConfig, StartupConfig
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.models import User


class DetailForm(forms.ModelForm):
    class Meta:
        model = StartupConfig
        fields = ("__all__")

        # change labels for offsets
        labels = {
            "sunrise_offset": "Sunrise",
            "sunset_offset": "Sunset",
        }


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = ("__all__")


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ('username','password')