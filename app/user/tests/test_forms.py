"""
Tests for user forms.
"""

from django.test import TestCase
from user.forms import UserRegisterForm


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
