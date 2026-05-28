"""
Tests for user views.
"""

from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

REGISTER_URL = reverse("user:register")


class PublicUserViewsTests(TestCase):
    """Test public user views."""

    def test_register_page_successful(self):
        """Test register page is displayed."""
        res = self.client.get(REGISTER_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "registration/register.html")
