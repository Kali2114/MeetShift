"""
Tests for user views.
"""

import tempfile
from http import HTTPStatus
from unittest.mock import patch

from core.models import Conversation, Message, Notification, User
from core.tests import utils
from django.contrib.auth.tokens import default_token_generator
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from user.utils import get_activate_account_url

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

    def test_register_view_creates_inactive_user(self):
        """Test register view creates inactive user."""
        payload = {
            "email": "test@example.com",
            "name": "testuser",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }

        res = self.client.post(REGISTER_URL, payload)

        user = User.objects.get(email=payload["email"])

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertFalse(user.is_active)

    @patch("user.views.send_activation_email_task.delay")
    def test_register_view_sends_activation_email_task(self, mock_send_activation_task):
        """Test register view sends activation email task."""
        payload = {
            "email": "test@example.com",
            "name": "testuser",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }

        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        mock_send_activation_task.assert_called_once()

    def test_activate_account_success(self):
        """Test user account can be activated with valid token."""
        user = utils.create_user(
            email="inactive@example.com",
            name="inactive",
        )
        user.is_active = False
        user.save(update_fields=["is_active"])

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        res = self.client.get(get_activate_account_url(uidb64, token))

        user.refresh_from_db()
        messages = list(res.wsgi_request._messages)

        self.assertEqual(
            str(messages[0]),
            "Your account has been activated. You can now log in.",
        )
        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertTrue(user.is_active)

    def test_activate_account_invalid_token(self):
        """Test user account is not activated with invalid token."""
        user = utils.create_user(
            email="inactive@example.com",
            name="inactive",
        )
        user.is_active = False
        user.save(update_fields=["is_active"])

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        res = self.client.get(get_activate_account_url(uidb64, "bad-token"))

        user.refresh_from_db()

        messages = list(res.wsgi_request._messages)

        self.assertEqual(
            str(messages[0]),
            "Activation link is invalid.",
        )
        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertFalse(user.is_active)

    def test_activate_account_invalid_uid(self):
        """Test invalid uid does not activate account."""
        res = self.client.get(get_activate_account_url("bad-uid", "bad-token"))

        self.assertEqual(res.status_code, HTTPStatus.FOUND)


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

    def test_user_can_read_message_notification(self):
        """Test reading a message notification redirects to the conversation."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)
        notification = utils.create_notification(
            user=self.user,
            conversation=conversation,
            message="New message from other.",
        )

        res = self.client.get(get_notification_read_url(notification.id))
        notification.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertTrue(notification.is_read)
        self.assertRedirects(
            res,
            reverse("user:conversation-detail", args=[conversation.id]),
        )

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

    def test_conversation_list_requires_login(self):
        """Test conversation list page requires login."""
        self.client.logout()
        conversation_list_url = reverse("user:conversation-list")

        res = self.client.get(conversation_list_url)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertRedirects(res, f"{reverse('login')}?next={conversation_list_url}")

    def test_conversation_list_page_displayed(self):
        """Test conversation list page is displayed."""
        conversation_list_url = reverse("user:conversation-list")

        res = self.client.get(conversation_list_url)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/conversation_list.html")

    def test_conversation_list_shows_only_own_conversations(self):
        """Test conversation list shows only conversations current user is part of."""
        other_user1 = utils.create_user(name="other1", email="other1@example.com")
        other_user2 = utils.create_user(name="other2", email="other2@example.com")
        own_conversation = utils.create_conversation(self.user, other_user1)
        utils.create_conversation(other_user1, other_user2)

        res = self.client.get(reverse("user:conversation-list"))

        self.assertEqual(
            list(res.context["conversations"]),
            [own_conversation],
        )

    def test_conversation_list_orders_by_latest_activity(self):
        """Test conversation list is ordered by most recent message first."""
        other_user1 = utils.create_user(name="other1", email="other1@example.com")
        other_user2 = utils.create_user(name="other2", email="other2@example.com")
        older_conversation = utils.create_conversation(self.user, other_user1)
        newer_conversation = utils.create_conversation(self.user, other_user2)

        utils.create_message(
            conversation=older_conversation, sender=self.user, content="hi"
        )
        utils.create_message(
            conversation=newer_conversation, sender=self.user, content="hey"
        )

        res = self.client.get(reverse("user:conversation-list"))

        self.assertEqual(
            list(res.context["conversations"]),
            [newer_conversation, older_conversation],
        )

    def test_conversation_list_shows_unread_count(self):
        """Test conversation list annotates unread message count per conversation."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)

        utils.create_message(
            conversation=conversation, sender=other_user, content="unread 1"
        )
        utils.create_message(
            conversation=conversation, sender=other_user, content="unread 2"
        )
        utils.create_message(
            conversation=conversation,
            sender=self.user,
            content="own message, not counted",
        )

        res = self.client.get(reverse("user:conversation-list"))

        self.assertEqual(res.context["conversations"][0].unread_count, 2)

    def test_conversation_detail_requires_login(self):
        """Test conversation detail page requires login."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)
        self.client.logout()
        detail_url = reverse("user:conversation-detail", args=[conversation.id])

        res = self.client.get(detail_url)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertRedirects(res, f"{reverse('login')}?next={detail_url}")

    def test_conversation_detail_shows_messages(self):
        """Test conversation detail page shows the conversation's messages."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)
        utils.create_message(
            conversation=conversation, sender=other_user, content="Hello there!"
        )

        res = self.client.get(
            reverse("user:conversation-detail", args=[conversation.id])
        )

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/conversation_detail.html")
        self.assertContains(res, "Hello there!")

    def test_conversation_detail_includes_conversations_sidebar_context(self):
        """Test conversation detail page context includes the sidebar list."""
        other_user = utils.create_user(name="other", email="other@example.com")
        other_conversation = utils.create_conversation(self.user, other_user)
        third_user = utils.create_user(name="third", email="third@example.com")
        another_conversation = utils.create_conversation(self.user, third_user)

        res = self.client.get(
            reverse("user:conversation-detail", args=[other_conversation.id])
        )

        self.assertEqual(
            set(res.context["conversations"]),
            {other_conversation, another_conversation},
        )

    def test_conversation_detail_sidebar_conversations_have_other_user(self):
        """Test each sidebar conversation has the other participant attached."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)

        res = self.client.get(
            reverse("user:conversation-detail", args=[conversation.id])
        )

        sidebar_conversation = res.context["conversations"][0]
        self.assertEqual(sidebar_conversation.other_user, other_user)

    def test_conversation_detail_marks_active_conversation(self):
        """Test the open conversation id is exposed for sidebar highlighting."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)

        res = self.client.get(
            reverse("user:conversation-detail", args=[conversation.id])
        )

        self.assertEqual(res.context["active_conversation_id"], conversation.id)

    def test_conversation_detail_denies_non_participant(self):
        """Test conversation detail page 404s for a non-participant."""
        other_user1 = utils.create_user(name="other1", email="other1@example.com")
        other_user2 = utils.create_user(name="other2", email="other2@example.com")
        conversation = utils.create_conversation(other_user1, other_user2)

        res = self.client.get(
            reverse("user:conversation-detail", args=[conversation.id])
        )

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

    def test_conversation_detail_marks_other_users_messages_as_read(self):
        """Test viewing conversation marks other participant's messages read."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)
        incoming = utils.create_message(
            conversation=conversation, sender=other_user, content="incoming"
        )
        own = utils.create_message(
            conversation=conversation, sender=self.user, content="own"
        )

        self.client.get(reverse("user:conversation-detail", args=[conversation.id]))

        incoming.refresh_from_db()
        own.refresh_from_db()
        self.assertTrue(incoming.is_read)
        self.assertFalse(own.is_read)

    def test_send_message_requires_login(self):
        """Test sending a message requires login."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)
        self.client.logout()

        res = self.client.post(
            reverse("user:message-send", args=[conversation.id]),
            {"content": "hi"},
        )

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertTrue(res.url.startswith(reverse("login")))

    def test_send_message_creates_message_and_redirects(self):
        """Test sending a message creates it and redirects to the thread."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)

        res = self.client.post(
            reverse("user:message-send", args=[conversation.id]),
            {"content": "Hello!"},
        )

        self.assertRedirects(
            res, reverse("user:conversation-detail", args=[conversation.id])
        )
        self.assertTrue(
            Message.objects.filter(
                conversation=conversation, sender=self.user, content="Hello!"
            ).exists()
        )

    def test_send_message_creates_notification_for_recipient(self):
        """Test sending a message creates a notification for the recipient."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)

        self.client.post(
            reverse("user:message-send", args=[conversation.id]),
            {"content": "Hello!"},
        )

        self.assertTrue(
            Notification.objects.filter(
                user=other_user,
                conversation=conversation,
                meeting=None,
            ).exists()
        )

    def test_send_message_denies_non_participant(self):
        """Test sending a message to a conversation you're not part of fails."""
        other_user1 = utils.create_user(name="other1", email="other1@example.com")
        other_user2 = utils.create_user(name="other2", email="other2@example.com")
        conversation = utils.create_conversation(other_user1, other_user2)

        res = self.client.post(
            reverse("user:message-send", args=[conversation.id]),
            {"content": "hi"},
        )

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        self.assertFalse(Message.objects.filter(conversation=conversation).exists())

    def test_send_message_rejects_empty_content(self):
        """Test sending an empty message does not create it."""
        other_user = utils.create_user(name="other", email="other@example.com")
        conversation = utils.create_conversation(self.user, other_user)

        self.client.post(
            reverse("user:message-send", args=[conversation.id]),
            {"content": ""},
        )

        self.assertFalse(Message.objects.filter(conversation=conversation).exists())

    def test_conversation_start_requires_login(self):
        """Test starting a conversation requires login."""
        other_user = utils.create_user(name="other", email="other@example.com")
        self.client.logout()

        res = self.client.get(reverse("user:conversation-start", args=[other_user.id]))

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertTrue(res.url.startswith(reverse("login")))

    def test_conversation_start_creates_conversation_and_redirects(self):
        """Test starting a conversation creates it and redirects to the thread."""
        other_user = utils.create_user(name="other", email="other@example.com")

        res = self.client.get(reverse("user:conversation-start", args=[other_user.id]))

        conversation = Conversation.objects.get_or_create_between(
            self.user, other_user
        )[0]
        self.assertRedirects(
            res, reverse("user:conversation-detail", args=[conversation.id])
        )

    def test_conversation_start_reuses_existing_conversation(self):
        """Test starting a conversation twice reuses the same conversation."""
        other_user = utils.create_user(name="other", email="other@example.com")
        existing = utils.create_conversation(self.user, other_user)

        res = self.client.get(reverse("user:conversation-start", args=[other_user.id]))

        self.assertRedirects(
            res, reverse("user:conversation-detail", args=[existing.id])
        )
        self.assertEqual(Conversation.objects.count(), 1)

    def test_conversation_start_with_self_redirects_to_list(self):
        """Test starting a conversation with yourself is rejected."""
        res = self.client.get(reverse("user:conversation-start", args=[self.user.id]))

        self.assertRedirects(res, reverse("user:conversation-list"))
        self.assertEqual(Conversation.objects.count(), 0)

    def test_new_message_page_requires_login(self):
        """Test new message page requires login."""
        self.client.logout()
        new_message_url = reverse("user:new-message")

        res = self.client.get(new_message_url)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertRedirects(res, f"{reverse('login')}?next={new_message_url}")

    def test_new_message_page_lists_other_users(self):
        """Test new message page lists users other than the current user."""
        other_user = utils.create_user(name="other", email="other@example.com")

        res = self.client.get(reverse("user:new-message"))

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "user/new_message.html")
        self.assertIn(other_user, res.context["users"])
        self.assertNotIn(self.user, res.context["users"])

    def test_new_message_page_has_search_input(self):
        """Test new message page renders a search input for filtering users."""
        utils.create_user(name="other", email="other@example.com")

        res = self.client.get(reverse("user:new-message"))

        self.assertContains(res, 'id="new-message-search"')

    def test_profile_detail_shows_message_button_for_other_user(self):
        """Test profile detail page shows a message button for another user."""
        other_user = utils.create_user(name="other", email="other@example.com")

        res = self.client.get(get_user_detail_url(other_user.id))

        self.assertContains(
            res, reverse("user:conversation-start", args=[other_user.id])
        )

    def test_profile_detail_hides_message_button_for_own_profile(self):
        """Test profile detail page hides message button on your own profile."""
        res = self.client.get(USER_PROFILE_URL)

        self.assertNotContains(
            res, reverse("user:conversation-start", args=[self.user.id])
        )
