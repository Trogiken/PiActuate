from django import forms
from .models import SystemConfig


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        exclude = ['first_login']  # remember to save this value when database is updated, otherwise it will be reset to False

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