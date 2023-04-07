from django import forms
from .models import SystemConfig


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