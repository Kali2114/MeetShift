"""
Tests for user views.
"""

import tempfile
from http import HTTPStatus

from core.models import User
from core.tests import utils
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

REGISTER_URL = reverse("user:register")
USER_PROFILE_URL = reverse("user:profile")
USER_EDIT_PROFILE_URL = reverse("user:profile-edit")
USER_ACCOUNT_SETTINGS_URL = reverse("user:account-settings")
USER_EDIT_URL = reverse("user:user-edit")
PASSWORD_CHANGE_URL = reverse("user:password-change")
USER_DELETE_URL = reverse("user:user-delete")
PASSWORD_RESET_URL = reverse("user:password-reset")
PASSWORD_RESET_DONE_URL = reverse("user:password-reset-done")
PASSWORD_RESET_COMPLETE_URL = reverse("user:password-reset-complete")
NOTIFICATION_LIST_URL = reverse("user:notification-list")


def get_user_detail_url(user_id):
    """Return user detail url."""
    return reverse("user:profile-detail", args=[user_id])


def get_notification_read_url(notification_id):
    """Return notification url."""
    return reverse("user:notification-read", args=[notification_id])


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

    def test_password_change_requires_login(self):
        """Test password change page requires login."""
        res = self.client.get(PASSWORD_CHANGE_URL)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_delete_user_requires_login(self):
        """Test delete user page requires login."""
        res = self.client.get(USER_DELETE_URL)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_password_reset_page_displayed(self):
        """Test password reset page is displayed."""
        res = self.client.get(PASSWORD_RESET_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/password_reset.html")

    def test_password_reset_done_page_displayed(self):
        """Test password reset done page is displayed."""
        res = self.client.get(PASSWORD_RESET_DONE_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/password_reset_done.html")

    def test_password_reset_complete_page_displayed(self):
        """Test password reset complete page is displayed."""
        res = self.client.get(PASSWORD_RESET_COMPLETE_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/password_reset_complete.html")

    def test_get_notification_requires_login(self):
        """Test notification read view requires login."""
        res = self.client.get(get_notification_read_url(5))

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            res,
            f"{reverse('login')}?next={get_notification_read_url(5)}",
        )

    def test_get_notification_list_requires_login(self):
        """Test get notification list view requires login."""
        res = self.client.get(NOTIFICATION_LIST_URL)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertRedirects(res, f"{reverse('login')}?next={NOTIFICATION_LIST_URL}")


class PrivateUserViewsTests(TestCase):
    """Test private user views."""

    def setUp(self):
        self.password = "Password"
        self.user = utils.create_user(password=self.password)
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
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertEqual(self.user.name, payload["name"])

    def test_edit_user_email(self):
        """Test user cannot edit own email."""
        payload = {
            "name": "for_fun",
            "email": "change_email",
        }
        old_email = self.user.email
        res = self.client.post(USER_EDIT_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertNotEqual(self.user.email, payload["email"])
        self.assertEqual(old_email, self.user.email)

    def test_password_change_page_displayed(self):
        """Test password change page displayed."""
        res = self.client.get(PASSWORD_CHANGE_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/password_change.html")

    def test_change_user_password(self):
        """Test user can change own password."""
        payload = {
            "old_password": self.password,
            "new_password1": "new_password123",
            "new_password2": "new_password123",
        }

        res = self.client.post(PASSWORD_CHANGE_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertTrue(self.user.check_password(payload["new_password1"]))

    def test_change_password_bad_credentials(self):
        """Test user cannot change password with bad credentials."""
        payload = {
            "old_password": "bad_password",
            "new_password1": "new_password123",
            "new_password2": "new_password123",
        }

        res = self.client.post(PASSWORD_CHANGE_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertFalse(self.user.check_password(payload["new_password1"]))
        self.assertTrue(self.user.check_password(self.password))
        self.assertTemplateUsed(res, "user/password_change.html")

    def test_change_password_too_short(self):
        """Test user cannot change password with too short."""
        payload = {
            "old_password": self.password,
            "new_password1": "dd",
            "new_password2": "dd",
        }
        res = self.client.post(PASSWORD_CHANGE_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertFalse(self.user.check_password(payload["new_password1"]))
        self.assertTrue(self.user.check_password(self.password))

    def test_change_password_entirely_numeric(self):
        """Test user cannot change password to entirely numeric password."""
        payload = {
            "old_password": self.password,
            "new_password1": "12345678",
            "new_password2": "12345678",
        }

        res = self.client.post(PASSWORD_CHANGE_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertFalse(self.user.check_password(payload["new_password1"]))
        self.assertTrue(self.user.check_password(self.password))

    def test_change_password_same_as_old_password(self):
        """Test user cannot change password to same old password."""
        payload = {
            "old_password": self.password,
            "new_password1": self.password,
            "new_password2": self.password,
        }

        res = self.client.post(PASSWORD_CHANGE_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(self.user.check_password(self.password))

    def test_delete_user_page_displayed(self):
        """Test user delete page displayed successfully."""
        res = self.client.get(USER_DELETE_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/user_delete.html")

    def test_delete_user(self):
        """Test user can delete user successfully."""
        user_id = self.user.id
        res = self.client.post(USER_DELETE_URL)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_user_password_reset(self):
        """Test password reset email can be requested."""
        payload = {
            "email": self.user.email,
        }
        res = self.client.post(PASSWORD_RESET_URL, payload)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_user_can_read_own_notification(self):
        """Test user can mark own notification as read."""
        organizer = utils.create_user(
            name="organizer",
            email="organizer@example.com",
        )
        meeting = utils.create_meeting(organizer=organizer)

        utils.create_meeting_participant(
            meeting=meeting,
            user=self.user,
        )

        notification = utils.create_notification(
            user=self.user,
            meeting=meeting,
        )

        res = self.client.get(get_notification_read_url(notification.id))
        notification.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertTrue(notification.is_read)
        self.assertRedirects(
            res,
            reverse("meeting:detail-meeting", args=[meeting.id]),
        )

    def test_user_cannot_read_other_notification(self):
        """Test user cannot mark other user's notification as read."""
        participant = utils.create_user(
            name="participant", email="participant@example.com"
        )
        meeting = utils.create_meeting(organizer=self.user)
        notification = utils.create_notification(
            user=participant, meeting=meeting, message="test_message"
        )
        res = self.client.get(get_notification_read_url(notification.id))
        notification.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        self.assertFalse(notification.is_read)

    def test_user_can_see_own_notification(self):
        """Test user can see own notifications successfully."""
        organizer = utils.create_user(
            name="organizer",
            email="organizer@example.com",
        )
        meeting = utils.create_meeting(organizer=organizer)
        notification = utils.create_notification(
            user=self.user, meeting=meeting, message="test_message"
        )
        res = self.client.get(NOTIFICATION_LIST_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertContains(res, notification.message)
        self.assertTemplateUsed(
            res,
            "user/notification_list.html",
        )

    def test_user_can_not_see_other_notifications(self):
        """Test user cannot see other user's notifications."""
        other_user = utils.create_user(
            name="other_user", email="other_user@example.com"
        )
        meeting = utils.create_meeting(organizer=self.user)
        notification = utils.create_notification(
            user=other_user, meeting=meeting, message="test_message"
        )
        res = self.client.get(NOTIFICATION_LIST_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertNotContains(res, notification.message)
