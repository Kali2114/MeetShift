"""
Tests for meeting forms.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from meeting.forms import MeetingForm


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
