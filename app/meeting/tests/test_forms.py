"""
Tests for meeting forms.
"""

from datetime import timedelta

from core.tests import utils
from django.test import TestCase
from django.utils import timezone
from meeting.forms import InviteParticipantForm, MeetingForm


class MeetingFormTests(TestCase):
    """Test meeting form."""

    def test_meeting_form_valid_with_correct_dates(self):
        """Test form is valid when end date is after start date."""
        started_at = timezone.now()
        ended_at = started_at + timedelta(hours=1)

        form = MeetingForm(
            data={
                "title": "Test meeting",
                "description": "Test description",
                "started_at": started_at,
                "ended_at": ended_at,
            }
        )

        self.assertTrue(form.is_valid())

    def test_meeting_form_invalid_when_end_before_start(self):
        """Test form is invalid when end date is before start date."""
        started_at = timezone.now()
        ended_at = started_at - timedelta(hours=1)

        form = MeetingForm(
            data={
                "title": "Test meeting",
                "description": "Test description",
                "started_at": started_at,
                "ended_at": ended_at,
            }
        )

        self.assertFalse(form.is_valid())

    def test_meeting_form_invalid_when_end_equals_start(self):
        """Test form is invalid when end date equals start date."""
        started_at = timezone.now()

        form = MeetingForm(
            data={
                "title": "Test meeting",
                "description": "Test description",
                "started_at": started_at,
                "ended_at": started_at,
            }
        )

        self.assertFalse(form.is_valid())


class InviteParticipantFormTests(TestCase):
    """Test invite participant form."""

    def test_invite_participant_form_valid(self):
        """Test invite participant form is valid."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        participant = utils.create_user(
            name="participant", email="participant@example.com"
        )
        meeting = utils.create_meeting(organizer=organizer)

        form = InviteParticipantForm(
            data={"email": participant.email},
            meeting=meeting,
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["user"], participant)

    def test_invite_non_existing_user_invalid(self):
        """Test invite form is invalid for non-existing user."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)

        form = InviteParticipantForm(
            data={"email": "missing@example.com"},
            meeting=meeting,
        )

        self.assertFalse(form.is_valid())

    def test_invite_organizer_invalid(self):
        """Test invite form is invalid for meeting organizer."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)

        form = InviteParticipantForm(
            data={"email": organizer.email},
            meeting=meeting,
        )

        self.assertFalse(form.is_valid())

    def test_invite_existing_participant_invalid(self):
        """Test invite form is invalid for existing participant."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        participant = utils.create_user(
            name="participant", email="participant@example.com"
        )
        meeting = utils.create_meeting(organizer=organizer)
        utils.create_meeting_participant(meeting=meeting, user=participant)

        form = InviteParticipantForm(
            data={"email": participant.email},
            meeting=meeting,
        )

        self.assertFalse(form.is_valid())
