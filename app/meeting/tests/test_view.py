"""
Tests for meeting views.
"""

from http import HTTPStatus

from core.tests import utils
from django.test import Client, TestCase
from django.urls import reverse

MEETING_LIST_URL = reverse("meeting:list")


class PublicMeetingViewsTests(TestCase):
    """Test unauthenticated view request."""

    def setUp(self):
        self.client = Client()

    def test_auth_required(self):
        """Test auth is required to retrieve meetings."""
        res = self.client.get(MEETING_LIST_URL)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)


class PrivateMeetingViewsTests(TestCase):
    """Test authenticated view request."""

    def setUp(self):
        self.client = Client()
        self.user = utils.create_user()
        self.client.force_login(self.user)

    def test_retrieve_meetings_successful(self):
        """Test retrieving meetings for logged-in user."""
        res = self.client.get(MEETING_LIST_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_list_meetings_for_logged_in_user(self):
        """Test list meetings related to logged-in user."""
        other_user = utils.create_user(email="other@example.com", name="other")

        organized_meeting = utils.create_meeting(organizer=self.user)

        participant_meeting = utils.create_meeting(organizer=other_user)
        utils.create_meeting_participant(
            meeting=participant_meeting,
            user=self.user,
        )

        other_meeting = utils.create_meeting(
            organizer=other_user,
            title="Other meeting",
        )

        res = self.client.get(MEETING_LIST_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertContains(res, organized_meeting.title)
        self.assertContains(res, participant_meeting.title)
        self.assertNotContains(res, other_meeting.title)
