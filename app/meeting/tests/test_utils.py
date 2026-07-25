"""
Tests for meeting utils.
"""

from datetime import timedelta

from core.tests import utils
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from meeting.utils import meeting_calendar_events


class MeetingCalendarEventsTests(TestCase):
    """Tests for meeting_calendar_events."""

    def test_excludes_meetings_without_start_time(self):
        """Test meetings without a start time are excluded."""
        organizer = utils.create_user()
        utils.create_meeting(organizer=organizer, title="no start")

        events = meeting_calendar_events(organizer)

        self.assertEqual(events, [])

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
