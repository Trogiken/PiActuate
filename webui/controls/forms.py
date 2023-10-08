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
    
    # pin validation based off of board mode
    def clean(self):
        cleaned_data = super().clean()
        board_mode = cleaned_data.get("board_mode")
        pins = range(2, 28) if board_mode == "BCM" else [3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33, 35, 36, 37, 38, 40]
        for i in range(1, 6):
            if cleaned_data.get(f"switch{i}") not in pins:
                self.add_error(f"switch{i}", f"Invalid Pin for '{board_mode}' Mode")
        for relay in ["relay1", "relay2"]:
            if cleaned_data.get(relay) not in pins:
                self.add_error(relay, f"Invalid Pin for '{board_mode}' Mode")


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ('username','password')