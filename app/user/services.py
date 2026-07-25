from core.models import Notification


def create_notification(*, user, meeting, message):
    """Create notification; WebSocket delivery is handled by core.signals."""
    return Notification.objects.create(
        user=user,
        meeting=meeting,
        message=message,
    )
