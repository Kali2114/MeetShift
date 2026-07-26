"""
Utils for meeting app.
"""

from core.models import Meeting, MeetingParticipant, RoomPresence, User
from django.db.models import Q
from django.templatetags.static import static
from django.urls import reverse

RESPONDED_STATUSES = ("ACC", "DEC")


def user_meetings_queryset(user):
    return (
        Meeting.objects.filter(Q(organizer=user) | Q(participants__user=user))
        .select_related("organizer")
        .prefetch_related(
            "participants", "participants__user", "participants__user__user_profile"
        )
        .distinct()
        .order_by("-created_at")
    )


def _participant_avatar_url(user):
    """Return the participant's avatar url, or a default placeholder."""
    if user.user_profile.avatar:
        return user.user_profile.avatar.url

    return static("img/no-avatar.jpg")


def meeting_calendar_events(user, avatar_limit=3):
    """Build calendar event data with responded-participant avatars."""
    events = []

    for meeting in user_meetings_queryset(user):
        if not meeting.started_at:
            continue

        responded = [
            participant
            for participant in meeting.participants.all()
            if participant.invitation_status in RESPONDED_STATUSES
        ]
        shown = responded[:avatar_limit]

        events.append(
            {
                "title": meeting.title,
                "start": meeting.started_at.isoformat(),
                "end": meeting.ended_at.isoformat() if meeting.ended_at else None,
                "url": reverse("meeting:detail-meeting", args=[meeting.id]),
                "participants": [
                    {
                        "name": participant.user.name,
                        "status": participant.invitation_status,
                        "avatar_url": _participant_avatar_url(participant.user),
                    }
                    for participant in shown
                ],
                "extra_count": max(len(responded) - avatar_limit, 0),
            }
        )

    return events


def user_accessible_room_meetings(user):
    """Return meetings whose room the user can access."""
    return Meeting.objects.filter(
        Q(organizer=user)
        | Q(participants__user=user, participants__invitation_status="ACC")
    ).distinct()


def mark_user_present(room, user):
    """Record a WebSocket connection for a user in a room."""
    presence, created = RoomPresence.objects.get_or_create(
        room=room, user=user, defaults={"connection_count": 1}
    )
    if not created:
        presence.connection_count += 1
        presence.save(update_fields=["connection_count"])


def mark_user_absent(room, user):
    """Remove one WebSocket connection for a user in a room."""
    try:
        presence = RoomPresence.objects.get(room=room, user=user)
    except RoomPresence.DoesNotExist:
        return

    if presence.connection_count <= 1:
        presence.delete()
    else:
        presence.connection_count -= 1
        presence.save(update_fields=["connection_count"])


def online_room_users(room):
    """Return users currently present in a room."""
    return User.objects.filter(room_presences__room=room).distinct()


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
