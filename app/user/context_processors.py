"""
Context processors for user app.
"""

from core.models import Message, Notification
from django.db.models import Q


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


def unread_messages_count(request):
    """Return unread message count for current user."""
    if not request.user.is_authenticated:
        return {"unread_messages_count": 0}

    return {
        "unread_messages_count": Message.objects.filter(
            Q(conversation__user1=request.user) | Q(conversation__user2=request.user),
            is_read=False,
        )
        .exclude(sender=request.user)
        .count()
    }
