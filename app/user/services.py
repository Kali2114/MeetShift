from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from core.models import Notification


def create_notification(*, user, meeting, message):
    """Create notification and send it to user's WebSocket group."""
    notification = Notification.objects.create(
        user=user,
        meeting=meeting,
        message=message,
    )

    unread_count = Notification.objects.filter(
        user=user,
        is_read=False,
    ).count()

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"notifications_user_{user.id}",
        {
            "type": "notification.message",
            "id": notification.id,
            "message": notification.message,
            "meeting_id": meeting.id,
            "unread_count": unread_count,
        },
    )

    return notification
