"""
Utils for meeting app.
"""

from core.models import Meeting
from django.db.models import Q


def user_meetings_queryset(user):
    return (
        Meeting.objects.filter(Q(organizer=user) | Q(participants__user=user))
        .distinct()
        .order_by("-created_at")
    )
