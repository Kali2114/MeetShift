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
    """Manager for users."""

    def create_user(self, email, name, password=None, **kwargs):
        """Create, save and return a new user."""
        normalized_email = self.normalize_email(email).strip().lower()
        check_email_and_name(normalized_email, name)

        user = self.model(
            email=normalized_email,
            name=name,
            **kwargs,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password=None, **kwargs):
        """Create, save and return a new superuser."""
        normalized_email = self.normalize_email(email).strip().lower()
        check_email_and_name(normalized_email, name)

        user = self.model(
            email=normalized_email,
            name=name,
            is_superuser=True,
            is_staff=True,
            **kwargs,
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


class UserProfile(models.Model):
    """Model for user profile."""

    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="user_profile"
    )
    avatar = models.ImageField(upload_to=avatar_file_path, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.name}"


class Meeting(models.Model):
    """Model for meeting object."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    organizer = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="organized_meetings"
    )
    status = models.CharField(max_length=3, choices=enums.STATUS_CHOICES, default="DRF")
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
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
    """Model for time slot response object."""

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


class Notification(models.Model):
    """Model for notification object."""

    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="notifications"
    )
    meeting = models.ForeignKey(
        "Meeting",
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    conversation = models.ForeignKey(
        "Conversation",
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message} to {self.user.name}"


class ConversationManager(models.Manager):
    """Manager for conversations."""

    def get_or_create_between(self, user_a, user_b):
        """Return the conversation between two users, creating it in canonical order."""
        user1, user2 = sorted([user_a, user_b], key=lambda u: u.pk)
        return self.get_or_create(user1=user1, user2=user2)


class Conversation(models.Model):
    """Model for conversation object."""

    user1 = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="conversations_user1"
    )
    user2 = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="conversations_user2"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ConversationManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"], name="unique_conversation_pair"
            ),
            models.CheckConstraint(
                condition=models.Q(user1_id__lt=models.F("user2_id")),
                name="conversation_user1_lt_user2",
            ),
        ]

    def __str__(self):
        return f"Conversation between {self.user1} and {self.user2}"

    def other_participant(self, user):
        """Return the participant that is not the given user."""
        return self.user2 if self.user1_id == user.id else self.user1


class Message(models.Model):
    """Model for message object."""

    conversation = models.ForeignKey(
        "Conversation", on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender} in conversation {self.conversation_id}"
