"""
Utils for meeting app.
"""

from core.models import Meeting, MeetingParticipant
from django.db.models import Q


def user_meetings_queryset(user):
    return (
        Meeting.objects.filter(Q(organizer=user) | Q(participants__user=user))
        .select_related("organizer")
        .prefetch_related("participants", "participants__user")
        .distinct()
        .order_by("-created_at")
    )


def user_has_meeting_conflict(user, meeting):
    """Check if user has accepted meeting in the same time."""
    return (
        MeetingParticipant.objects.filter(
            user=user,
            invitation_status="ACC",
            meeting__started_at__lt=meeting.ended_at,
            meeting__ended_at__gt=meeting.started_at,
        )
        .exclude(meeting=meeting)
        .exists()
    )
