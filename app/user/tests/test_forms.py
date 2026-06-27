"""
Tests for user forms.
"""

from core.tests import utils
from django.test import TestCase
from user.forms import (
    UserAuthenticationForm,
    UserEditForm,
    UserProfileForm,
    UserRegisterForm,
)


class UserRegisterFormTests(TestCase):
    """Test user register form."""

    def test_valid_register_form(self):
        """Test register form is valid with correct data."""
        form = UserRegisterForm(
            data={
                "email": "test@example.com",
                "name": "testuser",
                "password": "testpass123",
                "password_confirm": "testpass123",
            }
        )

        self.assertTrue(form.is_valid())

    def test_register_form_creates_user_with_hashed_password(self):
        """Test register form creates user with hashed password."""
        form = UserRegisterForm(
            data={
                "email": "test@example.com",
                "name": "testuser",
                "password": "testpass123",
                "password_confirm": "testpass123",
            }
        )

        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "testuser")
        self.assertTrue(user.check_password("testpass123"))

    def test_register_form_requires_email(self):
        """Test email is required."""
        form = UserRegisterForm(
            data={
                "email": "",
                "name": "testuser",
                "password": "testpass123",
                "password_confirm": "testpass123",
            }
        )

        self.assertFalse(form.is_valid())

    def test_register_form_requires_name(self):
        """Test name is required."""
        form = UserRegisterForm(
            data={
                "email": "test@example.com",
                "name": "",
                "password": "testpass123",
                "password_confirm": "testpass123",
            }
        )

        self.assertFalse(form.is_valid())

    def test_register_form_requires_password(self):
        """Test password is required."""
        form = UserRegisterForm(
            data={
                "email": "test@example.com",
                "name": "testuser",
                "password": "",
                "password_confirm": "",
            }
        )

        self.assertFalse(form.is_valid())

    def test_register_form_passwords_must_match(self):
        """Test form is invalid when passwords do not match."""
        form = UserRegisterForm(
            data={
                "email": "test@example.com",
                "name": "testuser",
                "password": "testpass123",
                "password_confirm": "wrongpass123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_register_form_requires_password_confirmation(self):
        """Test password confirmation is required."""
        form = UserRegisterForm(
            data={
                "email": "test@example.com",
                "name": "testuser",
                "password": "testpass123",
                "password_confirm": "",
            }
        )

        self.assertFalse(form.is_valid())

    def test_new_user_is_active_false(self):
        """Test new user is_active field is false."""
        form = UserRegisterForm(
            data={
                "email": "test@example.com",
                "name": "testuser",
                "password": "testpass123",
                "password_confirm": "testpass123",
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertFalse(user.is_active)


class UserProfileFormTests(TestCase):
    """Test user profile form."""

    def test_user_profile_form_valid_with_allowed_fields(self):
        """Test profile form is valid with allowed fields."""
        form = UserProfileForm(
            data={
                "bio": "Test bio",
            }
        )

        self.assertTrue(form.is_valid())

    def test_user_profile_form_has_only_allowed_fields(self):
        """Test profile form contains only allowed fields."""
        form = UserProfileForm()

        self.assertEqual(list(form.fields), ["bio", "avatar"])


class UserEditFormTests(TestCase):
    """Test user edit form."""

    def test_user_edit_form_valid_with_name(self):
        """Test user edit form is valid with name."""
        form = UserEditForm(
            data={
                "name": "New name",
            }
        )

        self.assertTrue(form.is_valid())

    def test_user_edit_form_requires_name(self):
        """Test user edit form requires name."""
        form = UserEditForm(
            data={
                "name": "",
            }
        )

        self.assertFalse(form.is_valid())

    def test_user_edit_form_has_only_allowed_fields(self):
        """Test user edit form contains only allowed fields."""
        form = UserEditForm()

        self.assertEqual(list(form.fields), ["name"])


class UserAuthenticationFormTests(TestCase):
    """Test user authentication form."""

    def test_inactive_user_login_is_invalid(self):
        """Test inactive user cannot log in."""
        user = utils.create_user(
            email="inactive@example.com",
            password="testpass123",
        )
        user.is_active = False
        user.save(update_fields=["is_active"])

        form = UserAuthenticationForm(
            request=None,
            data={
                "username": user.email,
                "password": "testpass123",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Your account is inactive. "
            "Please check your email and activate your account.",
            form.errors["__all__"],
        )

    def test_authentication_form_with_unknown_user_is_invalid(self):
        """Test authentication form is invalid for unknown user."""
        form = UserAuthenticationForm(
            request=None,
            data={
                "username": "unknown@example.com",
                "password": "testpass123",
            },
        )

        self.assertFalse(form.is_valid())

    def test_active_user_login_is_valid(self):
        """Test active user can log in."""
        user = utils.create_user(
            email="active@example.com",
            password="testpass123",
        )
        user.is_active = True
        user.save(update_fields=["is_active"])

        form = UserAuthenticationForm(
            request=None,
            data={
                "username": user.email,
                "password": "testpass123",
            },
        )

        self.assertTrue(form.is_valid())
