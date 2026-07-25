"""
Tests for user signals.
"""

from unittest.mock import MagicMock, patch

from core.models import Message, Notification, User, UserProfile
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

    @patch("core.signals.async_to_sync")
    @patch("core.signals.get_channel_layer")
    def test_notification_creation_sends_websocket_event(
        self,
        mock_get_channel_layer,
        mock_async_to_sync,
    ):
        """Test created notification sends WebSocket event."""
        channel_layer = MagicMock()
        group_send = MagicMock()

        mock_get_channel_layer.return_value = channel_layer
        mock_async_to_sync.return_value = group_send

        user = utils.create_user(
            name="Participant",
            email="participant@example.com",
        )
        organizer = utils.create_user(
            name="Organizer",
            email="organizer@example.com",
        )
        meeting = utils.create_meeting(
            organizer=organizer,
        )

        with self.captureOnCommitCallbacks(execute=True):
            notification = Notification.objects.create(
                user=user,
                meeting=meeting,
                message="You have been invited.",
            )

        mock_get_channel_layer.assert_called_once_with()

        mock_async_to_sync.assert_called_once_with(
            channel_layer.group_send,
        )

        group_send.assert_called_once_with(
            f"notifications_user_{user.id}",
            {
                "type": "notification.message",
                "id": notification.id,
                "message": notification.message,
                "meeting_id": meeting.id,
                "conversation_id": None,
                "unread_count": 1,
            },
        )

    @patch("core.signals.async_to_sync")
    @patch("core.signals.get_channel_layer")
    def test_conversation_notification_creation_sends_websocket_event(
        self,
        mock_get_channel_layer,
        mock_async_to_sync,
    ):
        """Test a conversation-based notification includes conversation_id."""
        channel_layer = MagicMock()
        group_send = MagicMock()

        mock_get_channel_layer.return_value = channel_layer
        mock_async_to_sync.return_value = group_send

        user = utils.create_user(
            name="Participant",
            email="participant@example.com",
        )
        other_user = utils.create_user(
            name="Other",
            email="other@example.com",
        )
        conversation = utils.create_conversation(user, other_user)

        with self.captureOnCommitCallbacks(execute=True):
            notification = Notification.objects.create(
                user=user,
                conversation=conversation,
                message="New message from Other.",
            )

        group_send.assert_called_once_with(
            f"notifications_user_{user.id}",
            {
                "type": "notification.message",
                "id": notification.id,
                "message": notification.message,
                "meeting_id": None,
                "conversation_id": conversation.id,
                "unread_count": 1,
            },
        )

    def test_notification_update_does_not_send_websocket_event(self):
        """Test updated notification does not send WebSocket event."""
        user = utils.create_user(
            name="test_name1",
            email="participant@example.com",
        )
        organizer = utils.create_user(
            name="test_name2",
            email="organizer@example.com",
        )
        meeting = utils.create_meeting(
            organizer=organizer,
        )

        notification = Notification.objects.create(
            user=user,
            meeting=meeting,
            message="You have been invited.",
        )

        with (
            patch("core.signals.get_channel_layer") as mock_get_channel_layer,
            patch("core.signals.async_to_sync") as mock_async_to_sync,
        ):
            notification.is_read = True
            notification.save()

        mock_get_channel_layer.assert_not_called()
        mock_async_to_sync.assert_not_called()

    @patch("core.signals.async_to_sync")
    @patch("core.signals.get_channel_layer")
    def test_message_creation_sends_websocket_event_to_recipient_only(
        self,
        mock_get_channel_layer,
        mock_async_to_sync,
    ):
        """Test created message sends WebSocket event only to the other participant."""
        channel_layer = MagicMock()
        group_send = MagicMock()

        mock_get_channel_layer.return_value = channel_layer
        mock_async_to_sync.return_value = group_send

        sender = utils.create_user(
            name="Sender",
            email="sender@example.com",
        )
        recipient = utils.create_user(
            name="Recipient",
            email="recipient@example.com",
        )
        conversation = utils.create_conversation(sender, recipient)

        with self.captureOnCommitCallbacks(execute=True):
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                content="Hello!",
            )

        mock_get_channel_layer.assert_called_once_with()

        mock_async_to_sync.assert_called_once_with(
            channel_layer.group_send,
        )

        group_send.assert_called_once_with(
            f"notifications_user_{recipient.id}",
            {
                "type": "conversation.update",
                "kind": "conversation_update",
                "id": message.id,
                "conversation_id": conversation.id,
                "message": message.content,
                "sender_name": sender.name,
                "unread_count": 1,
                "total_unread_count": 1,
            },
        )

    @patch("core.signals.async_to_sync")
    @patch("core.signals.get_channel_layer")
    def test_message_websocket_event_total_unread_count_spans_conversations(
        self,
        mock_get_channel_layer,
        mock_async_to_sync,
    ):
        """Test total_unread_count sums unread messages across all conversations."""
        group_send = MagicMock()
        mock_get_channel_layer.return_value = MagicMock()
        mock_async_to_sync.return_value = group_send

        recipient = utils.create_user(
            name="Recipient",
            email="recipient@example.com",
        )
        sender = utils.create_user(
            name="Sender",
            email="sender@example.com",
        )
        other_sender = utils.create_user(
            name="OtherSender",
            email="other-sender@example.com",
        )
        conversation = utils.create_conversation(sender, recipient)
        other_conversation = utils.create_conversation(other_sender, recipient)

        with self.captureOnCommitCallbacks(execute=True):
            Message.objects.create(
                conversation=other_conversation,
                sender=other_sender,
                content="From another conversation.",
            )

        with self.captureOnCommitCallbacks(execute=True):
            Message.objects.create(
                conversation=conversation,
                sender=sender,
                content="Hello!",
            )

        last_call_payload = group_send.call_args_list[-1][0][1]
        self.assertEqual(last_call_payload["unread_count"], 1)
        self.assertEqual(last_call_payload["total_unread_count"], 2)

    def test_message_update_does_not_send_websocket_event(self):
        """Test updated message does not send WebSocket event."""
        sender = utils.create_user(
            name="Sender",
            email="sender@example.com",
        )
        recipient = utils.create_user(
            name="Recipient",
            email="recipient@example.com",
        )
        conversation = utils.create_conversation(sender, recipient)

        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content="Hello!",
        )

        with (
            patch("core.signals.get_channel_layer") as mock_get_channel_layer,
            patch("core.signals.async_to_sync") as mock_async_to_sync,
        ):
            message.is_read = True
            message.save()

        mock_get_channel_layer.assert_not_called()
        mock_async_to_sync.assert_not_called()
