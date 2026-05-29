"""
Tests for meeting views.
"""

from http import HTTPStatus

from core.models import Meeting
from core.tests import utils
from django.test import Client, TestCase
from django.urls import reverse

INDEX_URL = reverse("meeting:index")
MEETING_LIST_URL = reverse("meeting:list")
MEETING_CREATE_URL = reverse("meeting:create-meeting")


def get_meeting_detail_url(meeting_id):
    """Return meeting detail url."""
    return reverse("meeting:detail-meeting", args=[meeting_id])


def get_meeting_edit_url(meeting_id):
    """Return meeting patch url."""
    return reverse("meeting:edit-meeting", args=[meeting_id])


def get_meeting_delete_url(meeting_id):
    """Return meeting delete url."""
    return reverse("meeting:delete-meeting", args=[meeting_id])


def get_meeting_invite_url(meeting_id):
    """Return meeting invite url."""
    return reverse("meeting:invite-participant", args=[meeting_id])


class PublicMeetingViewsTests(TestCase):
    """Test unauthenticated view request."""

    def setUp(self):
        self.client = Client()

    def test_auth_required(self):
        """Test auth is required to retrieve meetings."""
        res = self.client.get(MEETING_LIST_URL)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_index_auth_required(self):
        """Test auth is required to display index page."""
        res = self.client.get(INDEX_URL)

        self.assertEqual(res.status_code, HTTPStatus.FOUND)


class PrivateMeetingViewsTests(TestCase):
    """Test authenticated view request."""

    def setUp(self):
        self.client = Client()
        self.user = utils.create_user()
        self.client.force_login(self.user)

    def test_index_view_successful(self):
        """Test index page is displayed."""
        res = self.client.get(INDEX_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "index.html")

    def test_retrieve_meetings_successful(self):
        """Test retrieving meetings for logged-in user."""
        res = self.client.get(MEETING_LIST_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "meeting/meeting_list.html")

    def test_create_meeting_page_successful(self):
        """Test create meeting page is displayed."""
        res = self.client.get(MEETING_CREATE_URL)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "meeting/meeting_form.html")

    def test_edit_meeting_page_successful(self):
        """Test edit meeting page is displayed."""
        meeting = utils.create_meeting(organizer=self.user)

        res = self.client.get(get_meeting_edit_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "meeting/meeting_form.html")

    def test_delete_meeting_page_successful(self):
        """Test delete meeting confirmation page is displayed."""
        meeting = utils.create_meeting(organizer=self.user)

        res = self.client.get(get_meeting_delete_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "meeting/meeting_confirm_delete.html")

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
        self.assertTemplateUsed(res, "meeting/meeting_list.html")

    def test_organizer_can_view_meeting_detail(self):
        """Test organizer can view meeting detail."""
        meeting = utils.create_meeting(organizer=self.user)

        res = self.client.get(get_meeting_detail_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "meeting/meeting_details.html")
        self.assertEqual(res.context["meeting"], meeting)

    def test_participant_can_view_meeting_detail(self):
        """Test participant can view meeting detail."""
        organizer = utils.create_user(
            email="organizer@example.com",
            name="organizer",
        )
        meeting = utils.create_meeting(organizer=organizer)

        utils.create_meeting_participant(
            meeting=meeting,
            user=self.user,
        )

        res = self.client.get(get_meeting_detail_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res.context["meeting"], meeting)

    def test_other_user_cannot_view_meeting_detail(self):
        """Test user cannot view meeting they do not participate in."""
        other_user = utils.create_user(
            email="other@example.com",
            name="other",
        )
        meeting = utils.create_meeting(organizer=self.user)

        self.client.force_login(other_user)
        res = self.client.get(get_meeting_detail_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

    def test_non_existing_meeting_returns_404(self):
        """Test non-existing meeting detail returns 404."""
        res = self.client.get(get_meeting_detail_url(999))

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

    def test_create_view(self):
        """Test create view successful."""
        payload = {
            "title": "test_title",
            "description": "test_description",
        }
        res = self.client.post(MEETING_CREATE_URL, payload)

        meeting = Meeting.objects.get(title=payload["title"])
        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertEqual(meeting.description, payload["description"])
        self.assertEqual(meeting.organizer, self.user)
        self.assertRedirects(res, get_meeting_invite_url(meeting.id))

    def test_edit_meeting_by_organizer(self):
        """Test edit meeting by organizer successful."""
        meeting = utils.create_meeting(organizer=self.user)
        payload = {
            "title": "new_title",
            "description": "new_description",
        }
        res = self.client.post(get_meeting_edit_url(meeting.id), payload)
        meeting.refresh_from_db()

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.assertEqual(meeting.title, payload["title"])
        self.assertEqual(meeting.description, payload["description"])

    def test_edit_meeting_by_participant(self):
        """Test edit meeting by participant fail."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)
        utils.create_meeting_participant(meeting=meeting, user=self.user)
        payload = {
            "title": "new_title",
            "description": "new_description",
        }
        res = self.client.post(get_meeting_edit_url(meeting.id), payload)

        meeting.refresh_from_db()
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        self.assertNotEqual(meeting.title, payload["title"])
        self.assertNotEqual(meeting.description, payload["description"])

    def test_edit_meeting_by_another_user(self):
        """Test edit meeting by another user fail."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)
        payload = {
            "title": "new_title",
            "description": "new_description",
        }
        res = self.client.post(get_meeting_edit_url(meeting.id), payload)

        meeting.refresh_from_db()
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        self.assertNotEqual(meeting.title, payload["title"])
        self.assertNotEqual(meeting.description, payload["description"])

    def test_delete_meeting_by_organizer(self):
        """Test delete meeting by organizer successful."""
        meeting = utils.create_meeting(organizer=self.user)
        res = self.client.post(get_meeting_delete_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        meeting_exist = Meeting.objects.filter(id=meeting.id).exists()
        self.assertFalse(meeting_exist)

    def test_delete_meeting_by_participant(self):
        """Test delete meeting by participant fail."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)
        utils.create_meeting_participant(meeting=meeting, user=self.user)
        res = self.client.post(get_meeting_delete_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        meeting_exist = Meeting.objects.filter(id=meeting.id).exists()
        self.assertTrue(meeting_exist)

    def test_delete_meeting_by_another_user(self):
        """Test delete meeting by another user fail."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)
        res = self.client.post(get_meeting_delete_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        meeting_exist = Meeting.objects.filter(id=meeting.id).exists()
        self.assertTrue(meeting_exist)

    def test_organizer_display_invite_page(self):
        """Test organizer display invite page successful."""
        meeting = utils.create_meeting(organizer=self.user)
        res = self.client.get(get_meeting_invite_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "meeting/invite_participant.html")

    def test_participant_display_invite_page(self):
        """Test participant display invite page failed."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)
        utils.create_meeting_participant(meeting=meeting, user=self.user)
        res = self.client.get(get_meeting_invite_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

    def test_another_user_display_invite_page(self):
        """Test another user display invite page failed."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)
        res = self.client.get(get_meeting_invite_url(meeting.id))

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)

    def test_organizer_invite_user(self):
        """Test organizer invite user successful."""
        participant = utils.create_user(
            name="participant", email="participant@example.com"
        )
        meeting = utils.create_meeting(organizer=self.user)
        payload = {"users": [participant.id]}
        res = self.client.post(get_meeting_invite_url(meeting.id), payload)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTrue(meeting.participants.filter(user=participant).exists())

    def test_participant_invite_user(self):
        """Test participant invite user failed."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)
        another_user = utils.create_user(
            name="another_user", email="another@example.com"
        )
        utils.create_meeting_participant(meeting=meeting, user=self.user)
        payload = {"email": another_user.email}
        res = self.client.post(get_meeting_invite_url(meeting.id), payload)

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        self.assertFalse(meeting.participants.filter(user=another_user).exists())

    def test_another_user_invite_user(self):
        """Test another user invite user failed."""
        organizer = utils.create_user(name="organizer", email="organizer@example.com")
        meeting = utils.create_meeting(organizer=organizer)
        payload = {"email": self.user.email}
        res = self.client.post(get_meeting_invite_url(meeting.id), payload)

        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        self.assertFalse(meeting.participants.filter(user=self.user).exists())

    def test_invite_self_user(self):
        """Test invite self user failed."""
        meeting = utils.create_meeting(organizer=self.user)
        payload = {"email": self.user.email}
        res = self.client.post(get_meeting_invite_url(meeting.id), payload)

        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_invite_same_user_twice(self):
        """Test invite same user twice failed."""
        meeting = utils.create_meeting(organizer=self.user)
        participant = utils.create_user(
            name="participant", email="participant@example.com"
        )
        utils.create_meeting_participant(meeting=meeting, user=participant)
        payload = {"email": participant.email}
        res = self.client.post(get_meeting_invite_url(meeting.id), payload)

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(meeting.participants.filter(user=participant).count(), 1)
