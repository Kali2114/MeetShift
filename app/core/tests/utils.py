import io
from datetime import timedelta

from core import models
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image


def create_user(**params):
    """Create and return a new user."""
    default_user = {
        "email": "test@example.com",
        "password": "Test123",
        "name": "TestName",
    }
    default_user.update(**params)

    return get_user_model().objects.create_user(**default_user)


def create_test_image():
    """Create a dummy image for avatar."""
    image = Image.new("RGB", (100, 100), color="blue")
    byte_arr = io.BytesIO()
    image.save(byte_arr, format="PNG")
    byte_arr.seek(0)
    return SimpleUploadedFile("avatar.png", byte_arr.read(), content_type="image/png")


def create_meeting(**params):
    """Create and return a new meeting."""
    default_meeting = {
        "title": "test_title",
    }
    default_meeting.update(**params)
    return models.Meeting.objects.create(**default_meeting)


def create_meeting_participant(**params):
    """Create and return a new meeting participant."""
    return models.MeetingParticipant.objects.create(**params)


def create_time_slot_proposal(**params):
    """Create and return a new time slot proposal."""
    start_at = timezone.now()
    default_time_slot_proposal = {
        "start_at": start_at,
        "end_at": start_at + timedelta(hours=1),
    }
    default_time_slot_proposal.update(**params)
    return models.TimeSlotProposal.objects.create(**default_time_slot_proposal)


def create_time_slot_response(**params):
    """Create and return a new time slot response."""
    return models.TimeSlotResponse.objects.create(**params)
