"""
Forms for user app.
"""

from core.models import User, UserProfile
from django import forms


class UserRegisterForm(forms.ModelForm):
    """Form for user registration."""

    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "email", "password"]

    def clean(self):
        """Validate passwords match."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        """Create user with hashed password."""
        user = User(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
        )
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class UserProfileForm(forms.ModelForm):
    """Form for user profile."""

    class Meta:
        model = UserProfile
        fields = ["bio", "avatar"]


class UserEditForm(forms.ModelForm):
    """Form for editing user account."""

    class Meta:
        model = User
        fields = ["name"]
