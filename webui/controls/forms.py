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

        # TODO add labels and error messages
        labels = {
            # examples:
            "username": "Your name",
            "review_text": "Your review",
            "rating": "Your rating"
        }
        error_messages = {
            # examples:
            "username": {
                "required": "Please enter your name",
                "max_length": "Your name is too long"
            },
            "review_text": {
                "required": "Please enter your review"
            },
            "rating": {
                "required": "Please enter your rating",
                "min_value": "Please enter a rating of at least 1",
                "max_value": "Please enter a rating of at most 5"
            }
        }


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ('username','password')