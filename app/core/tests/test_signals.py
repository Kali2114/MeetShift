"""
Tests for signals.
"""

from core.models import UserProfile
from core.tests import utils
from django.test import TestCase


class SignalTests(TestCase):
    """Test signals."""

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
