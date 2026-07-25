"""
Tests for user context processors.
"""

from core.tests import utils
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from user.context_processors import unread_messages_count


class UnreadMessagesCountTests(TestCase):
    """Tests for unread_messages_count context processor."""

    def setUp(self):
        """Set up request used by the context processor."""
        self.request = RequestFactory().get("/")

    def test_returns_zero_for_anonymous_user(self):
        """Test anonymous user gets a zero count."""
        self.request.user = AnonymousUser()

        result = unread_messages_count(self.request)

        self.assertEqual(result["unread_messages_count"], 0)

    def test_counts_unread_messages_from_others_only(self):
        """Test count includes only unread messages from other participants."""
        user = utils.create_user()
        other_user = utils.create_user(email="other@example.com", name="other")
        conversation = utils.create_conversation(user, other_user)

        utils.create_message(conversation=conversation, sender=other_user, content="hi")
        utils.create_message(
            conversation=conversation, sender=other_user, content="hi again"
        )
        utils.create_message(
            conversation=conversation, sender=user, content="my own message"
        )

        self.request.user = user
        result = unread_messages_count(self.request)

        self.assertEqual(result["unread_messages_count"], 2)

    def test_excludes_read_messages(self):
        """Test count excludes already-read messages."""
        user = utils.create_user()
        other_user = utils.create_user(email="other@example.com", name="other")
        conversation = utils.create_conversation(user, other_user)

        utils.create_message(
            conversation=conversation,
            sender=other_user,
            content="already read",
            is_read=True,
        )

        self.request.user = user
        result = unread_messages_count(self.request)

        self.assertEqual(result["unread_messages_count"], 0)
