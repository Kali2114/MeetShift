"""
Tests for meeting utils.
"""

from datetime import timedelta

from core.models import RoomMessage, RoomPresence, RoomReadState
from core.tests import utils
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from meeting.utils import (
    SENDER_COLOR_PALETTE,
    mark_room_read,
    mark_user_absent,
    mark_user_present,
    meeting_calendar_events,
    online_room_users,
    room_notification_recipients,
    room_unread_count,
    sender_color,
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


class RoomUnreadCountTests(TestCase):
    """Tests for room unread message count and read-state tracking."""

    def test_room_unread_count_zero_with_no_messages(self):
        """Test unread count is zero when the room has no messages."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)

        self.assertEqual(room_unread_count(meeting.room, organizer), 0)

    def test_room_unread_count_counts_messages_never_read(self):
        """Test unread count includes all messages when never read."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        participant = utils.create_user(email="p@example.com", name="participant")
        utils.create_room_message(room=meeting.room, sender=participant, content="hi")
        utils.create_room_message(
            room=meeting.room, sender=participant, content="hi again"
        )

        self.assertEqual(room_unread_count(meeting.room, organizer), 2)

    def test_room_unread_count_excludes_own_messages(self):
        """Test a user's own messages never count as unread for them."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        utils.create_room_message(room=meeting.room, sender=organizer, content="hi")

        self.assertEqual(room_unread_count(meeting.room, organizer), 0)

    def test_room_unread_count_only_counts_messages_after_last_read(self):
        """Test messages sent before the last read time are not unread."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        participant = utils.create_user(email="p@example.com", name="participant")
        old_message = utils.create_room_message(
            room=meeting.room, sender=participant, content="old"
        )
        RoomMessage.objects.filter(pk=old_message.pk).update(
            created_at=timezone.now() - timedelta(hours=1)
        )
        utils.create_room_read_state(room=meeting.room, user=organizer)

        utils.create_room_message(room=meeting.room, sender=participant, content="new")

        self.assertEqual(room_unread_count(meeting.room, organizer), 1)

    def test_mark_room_read_creates_read_state(self):
        """Test marking a room read creates a read state row."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)

        mark_room_read(meeting.room, organizer)

        self.assertTrue(
            RoomReadState.objects.filter(room=meeting.room, user=organizer).exists()
        )

    def test_mark_room_read_updates_existing_read_state(self):
        """Test marking a room read again updates the row instead of duplicating."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        mark_room_read(meeting.room, organizer)

        mark_room_read(meeting.room, organizer)

        self.assertEqual(
            RoomReadState.objects.filter(room=meeting.room, user=organizer).count(), 1
        )

    def test_room_unread_count_zero_after_mark_room_read(self):
        """Test unread count resets to zero after marking the room read."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        participant = utils.create_user(email="p@example.com", name="participant")
        utils.create_room_message(room=meeting.room, sender=participant, content="hi")

        mark_room_read(meeting.room, organizer)

        self.assertEqual(room_unread_count(meeting.room, organizer), 0)


class SenderColorTests(TestCase):
    """Tests for the deterministic per-sender room chat color."""

    def test_sender_color_is_deterministic(self):
        """Test the same user id always returns the same color."""
        self.assertEqual(sender_color(7), sender_color(7))

    def test_sender_color_is_from_the_palette(self):
        """Test the returned color is always one of the palette entries."""
        self.assertIn(sender_color(42), SENDER_COLOR_PALETTE)

    def test_sender_color_differs_for_different_ids(self):
        """Test consecutive user ids get different colors from the palette."""
        self.assertNotEqual(sender_color(1), sender_color(2))


class RoomNotificationRecipientsTests(TestCase):
    """Tests for determining who to notify about new room activity."""

    def test_includes_organizer_when_not_sender(self):
        """Test the organizer is included when someone else sends a message."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        sender = utils.create_user(email="s@example.com", name="sender")
        utils.create_meeting_participant(
            meeting=meeting, user=sender, invitation_status="ACC"
        )

        recipients = room_notification_recipients(meeting, sender)

        self.assertEqual(recipients, {organizer})

    def test_excludes_sender_when_sender_is_organizer(self):
        """Test the organizer is excluded from their own notifications."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)

        recipients = room_notification_recipients(meeting, organizer)

        self.assertEqual(recipients, set())

    def test_includes_accepted_participants_excluding_sender(self):
        """Test accepted participants other than the sender are included."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        accepted = utils.create_user(email="a@example.com", name="accepted")
        utils.create_meeting_participant(
            meeting=meeting, user=accepted, invitation_status="ACC"
        )

        recipients = room_notification_recipients(meeting, organizer)

        self.assertEqual(recipients, {accepted})

    def test_excludes_pending_and_declined_participants(self):
        """Test pending and declined participants are never included."""
        organizer = utils.create_user()
        meeting = utils.create_meeting(organizer=organizer)
        pending = utils.create_user(email="p@example.com", name="pending")
        declined = utils.create_user(email="d@example.com", name="declined")
        utils.create_meeting_participant(
            meeting=meeting, user=pending, invitation_status="PND"
        )
        utils.create_meeting_participant(
            meeting=meeting, user=declined, invitation_status="DEC"
        )

        recipients = room_notification_recipients(meeting, organizer)

        self.assertEqual(recipients, set())
