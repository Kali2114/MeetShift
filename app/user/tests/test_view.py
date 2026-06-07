"""
Tests for user views.
"""

import tempfile
from http import HTTPStatus

from core.tests import utils
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

REGISTER_URL = reverse("user:register")
USER_PROFILE_URL = reverse("user:profile")
USER_EDIT_PROFILE_URL = reverse("user:profile-edit")
USER_ACCOUNT_SETTINGS_URL = reverse("user:account-settings")
USER_EDIT_URL = reverse("user:user-edit")


def get_user_detail_url(user_id):
    """Return user detail url."""
    return reverse("user:profile-detail", args=[user_id])


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

    def test_user_detail_page_requires_login(self):
        """Test user profile detail page requires login."""
        res = self.client.get(get_user_detail_url(1))

        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_user_account_settings_page_requires_login(self):
        """Test user account settings page requires login."""
        res = self.client.get(USER_ACCOUNT_SETTINGS_URL)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_edit_user_page_requires_login(self):
        """Test edit user page requires login."""
        res = self.client.get(USER_EDIT_URL)

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

    def test_user_profile_edit_with_id_not_found(self):
        """Test profile edit with user id does not exist."""
        another_user = utils.create_user(
            name="another_user",
            email="another@example.com",
        )

        res = self.client.get(f"/user/profile/{another_user.id}/edit/")

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_user_profile(self):
        """Test user profile cannot be deleted from edit view."""
        res = self.client.delete(USER_EDIT_PROFILE_URL)

        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_user_profile_delete_with_id_not_found(self):
        """Test profile delete with user id does not exist."""
        another_user = utils.create_user(
            name="another_user",
            email="another@example.com",
        )

        res = self.client.delete(f"/user/profile/{another_user.id}/delete/")

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
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

    def test_get_another_user_detail(self):
        """Test another user's profile detail page is displayed."""
        another_user = utils.create_user(
            name="another_user",
            email="another@example.com",
        )

        res = self.client.get(get_user_detail_url(another_user.id))

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/user_profile.html")
        self.assertEqual(res.context["profile"].user, another_user)

    def test_get_non_existing_user_detail_returns_not_found(self):
        """Test non-existing user profile detail returns 404."""
        res = self.client.get(get_user_detail_url(99))

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

    def test_get_user_setting_page(self):
        """Test user settings page is displayed."""
        res = self.client.get(USER_ACCOUNT_SETTINGS_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/account_settings.html")

    def test_get_edit_user_page(self):
        """Test edit user page is displayed."""
        res = self.client.get(USER_EDIT_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/user_edit.html")

    def test_edit_user_name(self):
        """Test user can edit own name."""
        payload = {"name": "change_name"}
        res = self.client.post(USER_EDIT_URL, payload)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(self.user.name, payload["name"])

    def test_edit_user_email(self):
        """Test user cannot edit own email."""
        payload = {"email": "change_email"}
        res = self.client.post(USER_EDIT_URL, payload)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertNotEqual(self.user.email, payload["email"])
