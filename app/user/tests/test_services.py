"""
Tests for user services.
"""

from core.models import Notification
from core.tests import utils
from django.test import TestCase
from user.services import create_notification


class CreateNotificationServiceTests(TestCase):
    """Tests for notification services."""

    def test_create_notification_creates_notification(self):
        """Test notification row is created with the given fields."""
        user = utils.create_user()
        organizer = utils.create_user(
            email="organizer@example.com",
            name="Organizer",
        )
        meeting = utils.create_meeting(organizer=organizer)

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

    def test_create_notification_with_conversation(self):
        """Test notification can be created with a conversation instead."""
        user = utils.create_user()
        other_user = utils.create_user(
            email="other@example.com",
            name="Other",
        )
        conversation = utils.create_conversation(user, other_user)

        notification = create_notification(
            user=user,
            conversation=conversation,
            message="New message from Other.",
        )

        self.assertTrue(
            Notification.objects.filter(
                id=notification.id,
                user=user,
                conversation=conversation,
                meeting=None,
                message="New message from Other.",
            ).exists()
        )
