"""
Tests for meeting utils.
"""

from datetime import timedelta

from core.models import RoomPresence
from core.tests import utils
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from meeting.utils import (
    mark_user_absent,
    mark_user_present,
    meeting_calendar_events,
    online_room_users,
)


class MeetingCalendarEventsTests(TestCase):
    """Tests for meeting_calendar_events."""

    def test_includes_basic_meeting_fields(self):
        """Test event includes title, url and an empty participant list."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(
            organizer=organizer,
            started_at=timezone.now(),
            ended_at=timezone.now() + timedelta(hours=1),
        )

        events = meeting_calendar_events(organizer)

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["title"], meeting.title)
        self.assertEqual(
            event["url"], reverse("meeting:detail-meeting", args=[meeting.id])
        )
        self.assertEqual(event["participants"], [])
        self.assertEqual(event["extra_count"], 0)

    def test_only_responded_participants_shown(self):
        """Test pending participants are excluded from the avatar list."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer, started_at=timezone.now())

        accepted_user = utils.create_user(email="a@example.com", name="accepted")
        declined_user = utils.create_user(email="d@example.com", name="declined")
        pending_user = utils.create_user(email="p@example.com", name="pending")

        utils.create_meeting_participant(
            meeting=meeting, user=accepted_user, invitation_status="ACC"
        )
        utils.create_meeting_participant(
            meeting=meeting, user=declined_user, invitation_status="DEC"
        )
        utils.create_meeting_participant(
            meeting=meeting, user=pending_user, invitation_status="PND"
        )

        events = meeting_calendar_events(organizer)
        participant_names = {p["name"] for p in events[0]["participants"]}

        self.assertEqual(participant_names, {"accepted", "declined"})
        self.assertEqual(events[0]["extra_count"], 0)

    def test_extra_count_for_responded_beyond_limit(self):
        """Test extra_count reflects responded participants beyond the limit."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer, started_at=timezone.now())

        for i in range(5):
            participant_user = utils.create_user(
                email=f"user{i}@example.com", name=f"user{i}"
            )
            utils.create_meeting_participant(
                meeting=meeting, user=participant_user, invitation_status="ACC"
            )

        events = meeting_calendar_events(organizer, avatar_limit=3)

        self.assertEqual(len(events[0]["participants"]), 3)
        self.assertEqual(events[0]["extra_count"], 2)

    def test_participant_status_included(self):
        """Test each participant entry includes its invitation status."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer, started_at=timezone.now())
        declined_user = utils.create_user(email="d@example.com", name="declined")
        utils.create_meeting_participant(
            meeting=meeting, user=declined_user, invitation_status="DEC"
        )

        events = meeting_calendar_events(organizer)

        self.assertEqual(events[0]["participants"][0]["status"], "DEC")

    def test_participant_avatar_url_uses_default_when_missing(self):
        """Test participant without an avatar gets the default avatar url."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer, started_at=timezone.now())
        participant_user = utils.create_user(email="p@example.com", name="participant")
        utils.create_meeting_participant(
            meeting=meeting, user=participant_user, invitation_status="ACC"
        )

        events = meeting_calendar_events(organizer)

        self.assertIn("no-avatar", events[0]["participants"][0]["avatar_url"])


class RoomPresenceTests(TestCase):
    """Tests for room presence tracking helpers."""

    def test_mark_user_present_creates_presence(self):
        """Test marking a user present creates a presence row."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)

        mark_user_present(meeting.room, organizer)

        presence = RoomPresence.objects.get(room=meeting.room, user=organizer)
        self.assertEqual(presence.connection_count, 1)

    def test_mark_user_present_twice_increments_count(self):
        """Test marking the same user present twice increments the count."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)

        mark_user_present(meeting.room, organizer)
        mark_user_present(meeting.room, organizer)

        presence = RoomPresence.objects.get(room=meeting.room, user=organizer)
        self.assertEqual(presence.connection_count, 2)

    def test_mark_user_absent_deletes_presence_at_zero(self):
        """Test marking a user absent removes the row once the count reaches zero."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)

        mark_user_present(meeting.room, organizer)
        mark_user_absent(meeting.room, organizer)

        self.assertFalse(
            RoomPresence.objects.filter(room=meeting.room, user=organizer).exists()
        )

    def test_mark_user_absent_keeps_presence_with_other_tabs_open(self):
        """Test marking one connection absent keeps the user online if others remain."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)

        mark_user_present(meeting.room, organizer)
        mark_user_present(meeting.room, organizer)
        mark_user_absent(meeting.room, organizer)

        presence = RoomPresence.objects.get(room=meeting.room, user=organizer)
        self.assertEqual(presence.connection_count, 1)

    def test_mark_user_absent_without_presence_does_nothing(self):
        """Test marking an already-absent user absent does not raise."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)

        mark_user_absent(meeting.room, organizer)

        self.assertFalse(RoomPresence.objects.exists())

    def test_online_room_users_returns_present_users(self):
        """Test online_room_users returns only users currently present."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        participant = utils.create_user(email="p@example.com", name="participant")
        utils.create_meeting_participant(
            meeting=meeting, user=participant, invitation_status="ACC"
        )

        mark_user_present(meeting.room, organizer)

        online_users = online_room_users(meeting.room)

        self.assertIn(organizer, online_users)
        self.assertNotIn(participant, online_users)
