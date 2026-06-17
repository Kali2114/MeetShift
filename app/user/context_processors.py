"""
Context processors for user app.
"""

from core.models import Notification


def unread_notifications_count(request):
    """Return unread notifications count for current user."""
    if not request.user.is_authenticated:
        return {"unread_notifications_count": 0}

    return {
        "unread_notifications_count": Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()
    }
