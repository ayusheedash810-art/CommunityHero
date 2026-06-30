from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Issue

class RegisterForm(UserCreationForm):

    email = forms.EmailField()

    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]
class IssueForm(forms.ModelForm):

    class Meta:
        model = Issue

        fields = [
            "title",
            "description",
            "image",
            "location",
        ]

        widgets = {

            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter issue title"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Describe the issue..."
            }),

            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter location"
            }),
        }