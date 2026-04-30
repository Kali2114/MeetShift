"""
Tests for models.
"""

from unittest.mock import patch

from core import models
from core.tests import utils
from django.contrib.auth import get_user_model
from django.test import TestCase


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
