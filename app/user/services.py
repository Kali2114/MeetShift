from core.models import Notification


def create_notification(*, user, message, meeting=None, conversation=None):
    """Create notification; WebSocket delivery is handled by core.signals."""
    return Notification.objects.create(
        user=user,
        meeting=meeting,
        conversation=conversation,
        message=message,
    )
