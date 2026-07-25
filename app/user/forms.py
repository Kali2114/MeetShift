"""
Forms for user app.
"""

from core.models import User, UserProfile
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password


class UserRegisterForm(forms.ModelForm):
    """Form for user registration."""

    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "email", "password"]

    def clean(self):
        """Validate passwords match and meet strength requirements."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        if password:
            temp_user = User(
                email=cleaned_data.get("email"),
                name=cleaned_data.get("name"),
            )
            try:
                validate_password(password, user=temp_user)
            except forms.ValidationError as error:
                self.add_error("password", error)

        return cleaned_data

    def save(self, commit=True):
        """Create user with hashed password."""
        user = User(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
        )
        user.set_password(self.cleaned_data["password"])
        user.is_active = False

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


class UserAuthenticationForm(AuthenticationForm):
    """Form for user authentication."""

    inactive_error = (
        "Your account is inactive. Please check your email and activate your account."
    )

    def clean(self):
        """Validate user credentials and active status."""
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                user = None

            if (
                user is not None
                and user.check_password(password)
                and not user.is_active
            ):
                raise forms.ValidationError(self.inactive_error)

        return super().clean()
