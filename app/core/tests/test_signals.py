"""
Tests for user signals.
"""

from unittest.mock import patch

from core.models import User, UserProfile
from core.tests import utils
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.test import RequestFactory, TestCase


class SignalTests(TestCase):
    """Test user signals."""

    def setUp(self):
        """Set up request used by authentication signals."""
        self.request = RequestFactory().get("/")

    def test_user_profile_created_after_user_creation(self):
        """Test user profile is created after user creation."""
        user = utils.create_user()

        self.assertTrue(hasattr(user, "user_profile"))
        self.assertEqual(user.user_profile.user, user)

    def test_user_profile_not_created_after_user_update(self):
        """Test user profile is not duplicated after user update."""
        user = utils.create_user()

        user.name = "Updated name"
        user.save()

        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)

    @patch("core.signals.logger")
    def test_successful_login_is_logged(self, mock_logger):
        """Test successful login is logged."""
        user = utils.create_user()

        user_logged_in.send(
            sender=User,
            request=self.request,
            user=user,
        )

        mock_logger.info.assert_called_once_with(
            "Authentication success user_id=%s",
            user.id,
        )

    @patch("core.signals.logger")
    def test_logout_is_logged(self, mock_logger):
        """Test authenticated user logout is logged."""
        user = utils.create_user()

        user_logged_out.send(
            sender=User,
            request=self.request,
            user=user,
        )

        mock_logger.info.assert_called_once_with(
            "User logged out user_id=%s",
            user.id,
        )

    @patch("core.signals.logger")
    def test_logout_without_user_is_not_logged(self, mock_logger):
        """Test logout without a user is not logged."""
        user_logged_out.send(
            sender=User,
            request=self.request,
            user=None,
        )

        mock_logger.info.assert_not_called()

    @patch("core.signals.logger")
    def test_failed_login_is_logged(self, mock_logger):
        """Test failed login attempt is logged."""
        user_login_failed.send(
            sender=User,
            credentials={
                "username": "user@example.com",
                "password": "wrong-password",
            },
            request=self.request,
        )

        mock_logger.warning.assert_called_once_with(
            "Authentication failed",
        )
