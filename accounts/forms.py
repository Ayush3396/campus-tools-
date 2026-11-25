"""
accounts/forms.py

Custom registration form that extends Django's built-in UserCreationForm.
UserCreationForm already handles password and password confirmation fields.
We add first_name, last_name, and email on top of it.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """
    Registration form for new students.

    Inherits from UserCreationForm which provides:
    - username field
    - password1 (password) field
    - password2 (confirm password) field
    - built-in password strength validation

    We add first_name, last_name, and email.
    """

    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'})
    )

    class Meta:
        # Tell Django which model and fields to use for this form
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def clean_email(self):
        """
        clean_<fieldname>() methods run field-level validation.
        Django calls them automatically during form.is_valid().
        If we raise ValidationError, the form is marked invalid.
        cleaned_data contains already-validated field values.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username
