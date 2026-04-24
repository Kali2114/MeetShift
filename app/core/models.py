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
