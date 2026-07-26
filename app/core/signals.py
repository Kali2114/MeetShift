"""
Signals for core app.
"""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from core.models import (
    Meeting,
    Message,
    Notification,
    Room,
    RoomMessage,
    User,
    UserProfile,
)
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger("core")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile after user creation."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Meeting)
def create_room(sender, instance, created, **kwargs):
    """Create room after meeting creation."""
    if created:
        Room.objects.create(meeting=instance)


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
            "conversation_id": notification.conversation_id,
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


def send_message_to_websocket(message_id):
    """Send message data to the other participant's WebSocket group."""
    message = Message.objects.select_related("conversation", "sender").get(
        id=message_id
    )
    conversation = message.conversation
    recipient = conversation.other_participant(message.sender)

    unread_count = (
        Message.objects.filter(
            conversation=conversation,
            is_read=False,
        )
        .exclude(sender=recipient)
        .count()
    )

    total_unread_count = (
        Message.objects.filter(
            Q(conversation__user1=recipient) | Q(conversation__user2=recipient),
            is_read=False,
        )
        .exclude(sender=recipient)
        .count()
    )

    group_name = f"notifications_user_{recipient.id}"

    logger.info(
        "Sending conversation update WebSocket event group=%s unread_count=%s",
        group_name,
        unread_count,
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "conversation.update",
            "kind": "conversation_update",
            "id": message.id,
            "conversation_id": conversation.id,
            "message": message.content,
            "sender_name": message.sender.name,
            "unread_count": unread_count,
            "total_unread_count": total_unread_count,
        },
    )


@receiver(post_save, sender=Message)
def send_message_websocket(sender, instance, created, **kwargs):
    """Send WebSocket event to the recipient after a message is committed."""
    if not created:
        return

    transaction.on_commit(lambda: send_message_to_websocket(instance.id))


def send_room_message_to_websocket(room_message_id):
    """Send room message data to the room's WebSocket group."""
    room_message = RoomMessage.objects.select_related("room", "sender").get(
        id=room_message_id
    )
    group_name = f"room_{room_message.room.meeting_id}"

    logger.info(
        "Sending room message WebSocket event group=%s",
        group_name,
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "room.message",
            "kind": "room_message",
            "id": room_message.id,
            "content": room_message.content,
            "sender_id": room_message.sender_id,
            "sender_name": room_message.sender.name,
        },
    )


@receiver(post_save, sender=RoomMessage)
def send_room_message_websocket(sender, instance, created, **kwargs):
    """Send WebSocket event to the room's group after a message is committed."""
    if not created:
        return

    transaction.on_commit(lambda: send_room_message_to_websocket(instance.id))
