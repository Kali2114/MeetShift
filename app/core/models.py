"""
Database models.
"""

import os
import uuid

from core import enums
from core.utils import check_email_and_name
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import (
    models,
)
from django.utils import timezone


def avatar_file_path(instance, filename):
    """Generate file path for user avatar."""
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads", "avatar", filename)


class UserManager(BaseUserManager):
    """Manage for users."""

    def create_user(self, email, name, password=None, **kwargs):
        """Create, save and return a new user."""
        check_email_and_name(email, name)
        user = self.model(email=self.normalize_email(email), name=name, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password=None, **kwargs):
        """Create, save and return a new superuser."""
        check_email_and_name(email, name)
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            is_superuser=True,
            is_staff=True,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


class Meeting(models.Model):
    """Model for meeting object."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    organizer = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="organized_meetings"
    )
    status = models.CharField(max_length=3, choices=enums.STATUS_CHOICES, default="DRF")
    started_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.organizer.name}"


class MeetingParticipant(models.Model):
    """Model for meeting participant object."""

    meeting = models.ForeignKey(
        "Meeting", on_delete=models.CASCADE, related_name="participants"
    )
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="meeting_participations"
    )
    role = models.CharField(max_length=3, choices=enums.ROLE_CHOICES, default="PRT")
    invitation_status = models.CharField(
        max_length=3, choices=enums.INVITATION_CHOICES, default="PND"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["meeting", "user"], name="unique_meeting_participant"
            )
        ]

    def __str__(self):
        return f"{self.user} in {self.meeting}"


class TimeSlotProposal(models.Model):
    """Model for time slot proposal object."""

    meeting = models.ForeignKey(
        "Meeting", on_delete=models.CASCADE, related_name="time_slot_proposals"
    )
    proposed_by = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="time_slot_proposals"
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_final = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_at__lt=models.F("end_at")),
                name="time_slot_start_before_end",
            )
        ]

    def __str__(self):
        return f"{self.meeting} from {self.start_at} to {self.end_at}"


class TimeSlotResponse(models.Model):
    proposal = models.ForeignKey(
        "TimeSlotProposal", on_delete=models.CASCADE, related_name="responses"
    )
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="time_slot_responses"
    )
    response = models.CharField(
        max_length=3, choices=enums.RESPONSE_CHOICES, default="MAY"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["proposal", "user"], name="unique_time_slot_response"
            )
        ]

    def __str__(self):
        return f"{self.response} by {self.user} to {self.proposal}"
