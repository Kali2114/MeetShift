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
            ["Test2@ExAmple.com", "Test2@example.com"],
            ["Test3@example.COM", "Test3@example.com"],
        ]
        for idx, (email, expected) in enumerate(sample_emails):
            user = utils.create_user(
                email=email,
                password="Test123",
                name=f"User{idx}",
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """Test raises ValueError when creating user without email."""
        with self.assertRaises(ValueError):
            utils.create_user(email="")

    def test_new_user_without_name_raise_error(self):
        """Test raises ValueError when creating user without email."""
        with self.assertRaises(ValueError):
            utils.create_user(name="")

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
