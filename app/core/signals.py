"""
Signals for core app.
"""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from core.models import Notification, User, UserProfile
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger("core")


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
    if user is None:
        return

    logger.info(
        "User logged out user_id=%s",
        user.id,
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log failed user login attempt."""
    logger.warning("Authentication failed")


def send_notification_to_websocket(notification_id):
    """Send notification data to user's WebSocket group."""
    notification = Notification.objects.get(id=notification_id)

    unread_count = Notification.objects.filter(
        user=notification.user,
        is_read=False,
    ).count()

    group_name = f"notifications_user_{notification.user_id}"

    logger.info(
        "Sending WebSocket event group=%s unread_count=%s",
        group_name,
        unread_count,
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "notification.message",
            "id": notification.id,
            "message": notification.message,
            "meeting_id": notification.meeting_id,
            "unread_count": unread_count,
        },
    )


@receiver(post_save, sender=Notification)
def send_notification_websocket(sender, instance, created, **kwargs):
    """Send WebSocket event after notification is committed."""
    logger.info(
        "Notification signal fired created=%s notification_id=%s user_id=%s",
        created,
        instance.id,
        instance.user_id,
    )

    if not created:
        return

    transaction.on_commit(lambda: send_notification_to_websocket(instance.id))
