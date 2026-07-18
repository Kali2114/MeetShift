"""
Tests for core views.
"""

from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    """Tests for health check endpoint."""

    def test_health_check_available_for_anonymous_user(self):
        """Test health check endpoint is available for anonymous user."""
        res = self.client.get(reverse("core:health-check"))

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res.json(), {"status": "ok", "database": "ok"})
