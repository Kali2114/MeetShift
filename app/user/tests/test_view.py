"""
Tests for user views.
"""

from http import HTTPStatus

from core.tests import utils
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

REGISTER_URL = reverse("user:register")
USER_PROFILE_URL = reverse("user:profile")
USER_EDIT_PROFILE_URL = reverse("user:profile-edit")


class PublicUserViewsTests(TestCase):
    """Test public user views."""

    def test_register_page_successful(self):
        """Test register page is displayed."""
        res = self.client.get(REGISTER_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "registration/register.html")

    def test_user_profile_page_requires_login(self):
        """Test user profile page requires login."""
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

    def test_user_profile_edit_page(self):
        """Test user edit profile page is displayed."""
        res = self.client.get(USER_EDIT_PROFILE_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/user_edit_profile.html")

    def test_user_profile_edit_updates_only_allowed_fields(self):
        """Test profile edit updates only allowed fields (bio)."""
        payload = {
            "name": "disallowed",
            "email": "hacked@gmail.com",
            "bio": "Hello, i changed my bio!",
        }
        res = self.client.post(USER_EDIT_PROFILE_URL, payload)
        self.user.refresh_from_db()
        self.user.user_profile.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertEqual(self.user.user_profile.bio, payload["bio"])
        self.assertNotEqual(self.user.email, payload["email"])
        self.assertNotEqual(self.user.name, payload["name"])

    def test_user_can_upload_avatar(self):
        """Test user can upload own avatar."""
        avatar = SimpleUploadedFile(
            name="avatar.gif",
            content=(
                b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00"
                b"\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00"
                b"\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )
        payload = {
            "avatar": avatar,
        }

        res = self.client.post(USER_EDIT_PROFILE_URL, payload)
        self.user.refresh_from_db()
        self.user.user_profile.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertTrue(self.user.user_profile.avatar.name)
        self.assertTrue(
            self.user.user_profile.avatar.name.startswith("uploads/avatar/")
        )
