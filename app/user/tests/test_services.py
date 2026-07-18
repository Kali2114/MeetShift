"""
Tests for user services.
"""

from unittest.mock import patch

from core.models import Notification
from core.tests import utils
from django.test import TestCase
from user.services import create_notification


class CreateNotificationServiceTests(TestCase):
    """Tests for notification services."""

    @patch("user.services.async_to_sync")
    @patch("user.services.get_channel_layer")
    def test_create_notification_creates_notification_and_sends_event(
        self,
        mock_get_channel_layer,
        mock_async_to_sync,
    ):
        """Test notification is created and WebSocket event is sent."""
        user = utils.create_user()
        organizer = utils.create_user(
            email="organizer@example.com",
            name="Organizer",
        )
        meeting = utils.create_meeting(organizer=organizer)

        channel_layer = mock_get_channel_layer.return_value
        group_send = mock_async_to_sync.return_value

        notification = create_notification(
            user=user,
            meeting=meeting,
            message="You have been invited.",
        )

        self.assertTrue(
            Notification.objects.filter(
                id=notification.id,
                user=user,
                meeting=meeting,
                message="You have been invited.",
            ).exists()
        )

        mock_async_to_sync.assert_called_once_with(channel_layer.group_send)

        group_send.assert_called_once_with(
            f"notifications_user_{user.id}",
            {
                "type": "notification.message",
                "id": notification.id,
                "message": notification.message,
                "meeting_id": meeting.id,
                "unread_count": 1,
            },
        )
