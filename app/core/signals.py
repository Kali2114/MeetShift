"""
Signals for user app.
"""

import logging

from core.models import User, UserProfile
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger("user")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile after user creation."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login."""
    logger.info(
        "Authentication success user_id=%s",
        user.id,
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    if user is not None:
        logger.info(
            "User logged out user_id=%s",
            user.id,
        )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log failed user login attempt."""
    logger.warning("Authentication failed")
