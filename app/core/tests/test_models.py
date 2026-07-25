"""
Tests for models.
"""

from datetime import timedelta
from unittest.mock import patch

from core import models
from core.tests import utils
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with email is successful."""
        email = "test@example.com"
        password = "Test123"

        user = utils.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email is normalized for new users."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@ExAmple.com", "test2@example.com"],
            ["Test3@example.COM", "test3@example.com"],
            ["  USER@EXAMPLE.COM  ", "user@example.com"],
        ]
        for idx, (email, expected) in enumerate(sample_emails):
            user = utils.create_user(
                email=email,
                password="Test123",
                name=f"User{idx}",
            )
            self.assertEqual(user.email, expected)

    def test_email_is_unique_case_insensitive(self):
        """Test users cannot use emails differing only by letter case."""
        utils.create_user(
            email="user@example.com",
            name="User One",
        )

        with self.assertRaises(IntegrityError):
            utils.create_user(
                email="USER@EXAMPLE.COM",
                name="User Two",
            )

    def test_new_user_without_email_raise_error(self):
        """Test raises ValueError when creating user without email."""
        with self.assertRaises(ValueError):
            utils.create_user(email="")

    def test_new_user_without_name_raise_error(self):
        """Test raises ValueError when creating user without email."""
        with self.assertRaises(ValueError):
            utils.create_user(name="")

    def test_new_user_with_invalid_email_raise_error(self):
        """Test raises ValueError when creating user with malformed email."""
        with self.assertRaises(ValueError):
            utils.create_user(email="not-an-email")

    def test_create_superuser(self):
        """Test creating a superuser successful."""
        user = get_user_model().objects.create_superuser(
            email="example@test.com",
            password="Test123",
            name="Test_Name",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    @patch("core.models.uuid.uuid4")
    def test_generate_image_path(self, mock_uuid):
        """Test generating path for image is successful."""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.avatar_file_path(None, "example.jpg")

        self.assertEqual(file_path, f"uploads/avatar/{uuid}.jpg")

    def test_create_meeting(self):
        """Test creating meeting successful."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)

        self.assertEqual(str(meeting), f"{meeting.title} by {organizer.name}")

    def test_create_meeting_participant(self):
        """Test creating meeting participant successful."""
        user = utils.create_user(email="user@example.com", name="test_user")
        organizer = utils.create_user(
            email="organizer@example.com", name="test_organizer"
        )
        meeting = utils.create_meeting(organizer=organizer)
        meeting_participant = utils.create_meeting_participant(
            meeting=meeting, user=user
        )

        self.assertEqual(
            str(meeting_participant),
            f"{meeting_participant.user} in {meeting_participant.meeting}",
        )

    def test_added_the_same_user_twice_times_error(self):
        """Test adding the same user twice times raise error."""
        user = utils.create_user(email="user@example.com", name="test_user")
        organizer = utils.create_user(
            email="organizer@example.com", name="test_organizer"
        )
        meeting = utils.create_meeting(organizer=organizer)
        utils.create_meeting_participant(meeting=meeting, user=user)

        with self.assertRaises(IntegrityError):
            utils.create_meeting_participant(meeting=meeting, user=user)

    def test_create_time_slot_proposal(self):
        """Test creating time slot proposal successful."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        time_slot_proposal = utils.create_time_slot_proposal(
            meeting=meeting,
            proposed_by=organizer,
        )
        self.assertEqual(
            str(time_slot_proposal),
            f"{time_slot_proposal.meeting} from "
            f"{time_slot_proposal.start_at} to {time_slot_proposal.end_at}",
        )

    def test_create_time_slot_proposal_start_after_end_error(self):
        """Test creating time slot proposal with start_at after end_at raises error."""
        organizer = utils.create_user()
        end_at = timezone.now()
        start_at = end_at + timedelta(hours=1)
        meeting = utils.create_meeting(organizer=organizer)

        with self.assertRaises(IntegrityError):
            utils.create_time_slot_proposal(
                meeting=meeting,
                proposed_by=organizer,
                start_at=start_at,
                end_at=end_at,
            )

    def test_create_time_slot_response(self):
        """Test creating time slot response successful."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        time_proposal = utils.create_time_slot_proposal(
            meeting=meeting, proposed_by=organizer
        )
        time_response = utils.create_time_slot_response(
            proposal=time_proposal, user=organizer
        )

        self.assertEqual(
            str(time_response),
            f"{time_response.response} by {organizer} to {time_proposal}",
        )

    def test_create_time_slot_response_twice_same_user_error(self):
        """Test creating time slot response by the same user twice times raise error."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        time_proposal = utils.create_time_slot_proposal(
            meeting=meeting, proposed_by=organizer
        )
        utils.create_time_slot_response(proposal=time_proposal, user=organizer)

        with self.assertRaises(IntegrityError):
            utils.create_time_slot_response(proposal=time_proposal, user=organizer)

    def test_create_user_profile(self):
        """Test creating user profile successful."""
        user = utils.create_user(email="user@gmail.com", name="test_user")

        self.assertEqual(str(user.user_profile), f"Profile of {user.name}")

    def test_create_notification(self):
        """Test creating notification successful."""
        user = utils.create_user(email="user@gmail.com", name="test_user")
        meeting = utils.create_meeting(organizer=user)
        notification = models.Notification.objects.create(
            user=user,
            meeting=meeting,
            message="Test_message",
        )

        self.assertEqual(str(notification), f"{notification.message} to {user.name}")

    def test_notification_default_is_unread(self):
        """Test notification is unread by default."""
        user = utils.create_user(email="user@gmail.com", name="test_user")

        notification = models.Notification.objects.create(
            user=user,
            message="Test message",
        )

        self.assertFalse(notification.is_read)

    def test_create_conversation(self):
        """Test creating conversation successful."""
        user_a = utils.create_user(email="a@example.com", name="user_a")
        user_b = utils.create_user(email="b@example.com", name="user_b")

        conversation = utils.create_conversation(user_a, user_b)

        self.assertEqual(
            str(conversation),
            f"Conversation between {conversation.user1} and {conversation.user2}",
        )

    def test_conversation_users_stored_in_canonical_order(self):
        """Test conversation always stores the lower-pk user as user1."""
        user_a = utils.create_user(email="a@example.com", name="user_a")
        user_b = utils.create_user(email="b@example.com", name="user_b")

        conversation_forward = utils.create_conversation(user_a, user_b)
        conversation_reversed = utils.create_conversation(user_b, user_a)

        self.assertEqual(conversation_forward.id, conversation_reversed.id)
        self.assertEqual(
            conversation_forward.user1, min(user_a, user_b, key=lambda u: u.pk)
        )

    def test_duplicate_conversation_pair_raises_error(self):
        """Test creating a duplicate conversation for the same pair raises error."""
        user_a = utils.create_user(email="a@example.com", name="user_a")
        user_b = utils.create_user(email="b@example.com", name="user_b")
        user1, user2 = sorted([user_a, user_b], key=lambda u: u.pk)

        models.Conversation.objects.create(user1=user1, user2=user2)

        with self.assertRaises(IntegrityError):
            models.Conversation.objects.create(user1=user1, user2=user2)

    def test_conversation_with_self_raises_error(self):
        """Test creating a conversation with the same user twice raises error."""
        user = utils.create_user()

        with self.assertRaises(IntegrityError):
            models.Conversation.objects.create(user1=user, user2=user)

    def test_create_message(self):
        """Test creating message successful."""
        user_a = utils.create_user(email="a@example.com", name="user_a")
        user_b = utils.create_user(email="b@example.com", name="user_b")
        conversation = utils.create_conversation(user_a, user_b)

        message = utils.create_message(
            conversation=conversation,
            sender=user_a,
            content="Hello!",
        )

        self.assertEqual(
            str(message),
            f"Message from {user_a} in conversation {conversation.id}",
        )

    def test_message_default_is_unread(self):
        """Test message is unread by default."""
        user_a = utils.create_user(email="a@example.com", name="user_a")
        user_b = utils.create_user(email="b@example.com", name="user_b")
        conversation = utils.create_conversation(user_a, user_b)

        message = utils.create_message(conversation=conversation, sender=user_a)

        self.assertFalse(message.is_read)

    def test_messages_ordered_by_created_at(self):
        """Test messages are returned in chronological order."""
        user_a = utils.create_user(email="a@example.com", name="user_a")
        user_b = utils.create_user(email="b@example.com", name="user_b")
        conversation = utils.create_conversation(user_a, user_b)

        first = utils.create_message(
            conversation=conversation, sender=user_a, content="first"
        )
        second = utils.create_message(
            conversation=conversation, sender=user_b, content="second"
        )

        self.assertEqual(list(conversation.messages.all()), [first, second])

    def test_conversation_other_participant(self):
        """Test other_participant returns the participant that isn't given."""
        user_a = utils.create_user(email="a@example.com", name="user_a")
        user_b = utils.create_user(email="b@example.com", name="user_b")
        conversation = utils.create_conversation(user_a, user_b)

        self.assertEqual(conversation.other_participant(user_a), user_b)
        self.assertEqual(conversation.other_participant(user_b), user_a)

    def test_create_notification_with_conversation(self):
        """Test notification can reference a conversation instead of a meeting."""
        user_a = utils.create_user(email="a@example.com", name="user_a")
        user_b = utils.create_user(email="b@example.com", name="user_b")
        conversation = utils.create_conversation(user_a, user_b)

        notification = models.Notification.objects.create(
            user=user_a,
            conversation=conversation,
            message="New message from user_b",
        )

        self.assertEqual(notification.conversation, conversation)
        self.assertIsNone(notification.meeting)
