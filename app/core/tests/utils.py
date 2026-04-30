import io

from core import models
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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
