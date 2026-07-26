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

    def test_meeting_form_requires_started_at(self):
        """Test form is invalid when started_at is missing."""
        form = MeetingForm(
            data={
                "title": "Test meeting",
                "description": "Test description",
                "ended_at": timezone.now() + timedelta(hours=1),
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("started_at", form.errors)

    def test_meeting_form_requires_ended_at(self):
        """Test form is invalid when ended_at is missing."""
        form = MeetingForm(
            data={
                "title": "Test meeting",
                "description": "Test description",
                "started_at": timezone.now(),
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("ended_at", form.errors)


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
            data={"users": [participant.id]},
            meeting=meeting,
        )

        self.assertTrue(form.is_valid())
        self.assertIn(participant, form.cleaned_data["users"])

    def test_invite_participant_form_requires_users(self):
        """Test invite participant form requires selected users."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)

        form = InviteParticipantForm(
            data={"users": []},
            meeting=meeting,
        )

        self.assertFalse(form.is_valid())

    def test_invite_form_excludes_organizer_from_users_queryset(self):
        """Test invite form excludes meeting organizer."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)

        form = InviteParticipantForm(meeting=meeting)

        self.assertNotIn(organizer, form.fields["users"].queryset)

    def test_invite_form_excludes_existing_participant_from_users_queryset(self):
        """Test invite form excludes existing meeting participant."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        participant = utils.create_user(
            name="participant", email="participant@example.com"
        )
        meeting = utils.create_meeting(organizer=organizer)
        utils.create_meeting_participant(meeting=meeting, user=participant)

        form = InviteParticipantForm(meeting=meeting)

        self.assertNotIn(participant, form.fields["users"].queryset)

    def test_invite_form_includes_available_user_in_users_queryset(self):
        """Test invite form includes available user."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        available_user = utils.create_user(
            name="available", email="available@example.com"
        )
        meeting = utils.create_meeting(organizer=organizer)

        form = InviteParticipantForm(meeting=meeting)

        self.assertIn(available_user, form.fields["users"].queryset)
