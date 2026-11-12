
import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


User = get_user_model()


class StudentRegistrationForm(forms.Form):

    full_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your full name"
        })
    )

    roll_number = forms.CharField(
        max_length=150,
        label="Roll Number",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your roll number"
        })
    )

    department = forms.CharField(
        max_length=100,
        label="Department",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your department"
        })
    )

    contact_number = forms.CharField(
        max_length=20,
        label="Contact Number",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your contact number"
        })
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your email"
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Create a password"
        }),
        strip=False
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Re-enter your password"
        }),
        strip=False
    )

    def clean_roll_number(self):
        roll_number = self.cleaned_data["roll_number"].strip()

        if User.objects.filter(username__iexact=roll_number).exists():
            raise forms.ValidationError(
                "This roll number is already registered."
            )

        return roll_number

    def clean_contact_number(self):
        number = self.cleaned_data["contact_number"].strip()

        if not re.fullmatch(r"\+?[0-9\s()-]+", number):
            raise forms.ValidationError(
                "Enter a valid contact number."
            )

        digits = re.sub(r"\D", "", number)

        if not 10 <= len(digits) <= 15:
            raise forms.ValidationError(
                "Contact number must contain 10 to 15 digits."
            )

        return number

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error(
                    "confirm_password",
                    "Passwords do not match."
                )

        if password:
            try:
                validate_password(password)
            except ValidationError as error:
                self.add_error("password", error)

        return cleaned_data
