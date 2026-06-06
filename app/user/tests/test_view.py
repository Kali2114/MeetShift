"""
Tests for user views.
"""

from http import HTTPStatus

from core.tests import utils
from django.test import TestCase
from django.urls import reverse

REGISTER_URL = reverse("user:register")
USER_PROFILE_URL = reverse("user:profile")


class PublicUserViewsTests(TestCase):
    """Test public user views."""

    def test_register_page_successful(self):
        """Test register page is displayed."""
        res = self.client.get(REGISTER_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "registration/register.html")

    def test_user_profile_page_requires_login(self):
        """Test user profile page not found by unauthorized user."""
        res = self.client.get(USER_PROFILE_URL)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)


class PrivateUserViewsTests(TestCase):
    """Test private user views."""

    def setUp(self):
        self.user = utils.create_user()
        self.client.force_login(self.user)

    def test_user_profile_page(self):
        """Test user profile page is displayed."""
        res = self.client.get(USER_PROFILE_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/user_profile.html")
