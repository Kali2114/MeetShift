"""
Tests for meeting consumers.
"""

from datetime import timedelta

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from core.tests import utils
from django.contrib.auth.models import AnonymousUser
from django.test import TransactionTestCase, override_settings
from django.utils import timezone
from meeting.routing import websocket_urlpatterns

TEST_CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
class RoomConsumerTests(TransactionTestCase):
    """Tests for room WebSocket consumer."""

    def setUp(self):
        """Create organizer and meeting for tests."""
        self.organizer = utils.create_user(
            name="organizer", email="organizer@example.com"
        )
        self.meeting = utils.create_meeting(
            organizer=self.organizer,
            started_at=timezone.now() - timedelta(minutes=5),
            ended_at=timezone.now() + timedelta(minutes=30),
        )

    async def connect(self, user, meeting_id=None):
        """Connect a communicator for the given user and meeting."""
        meeting_id = meeting_id or self.meeting.id
        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(application, f"/ws/room/{meeting_id}/")
        communicator.scope["user"] = user

        connected, _ = await communicator.connect()

        return communicator, connected

    async def test_organizer_can_connect(self):
        """Test organizer can connect to an active room."""
        communicator, connected = await self.connect(self.organizer)

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_accepted_participant_can_connect(self):
        """Test an accepted participant can connect to an active room."""
        participant = await sync_to_async(utils.create_user)(
            name="participant", email="participant@example.com"
        )
        await sync_to_async(utils.create_meeting_participant)(
            meeting=self.meeting, user=participant, invitation_status="ACC"
        )

        communicator, connected = await self.connect(participant)

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_anonymous_user_cannot_connect(self):
        """Test anonymous user cannot connect to a room."""
        communicator, connected = await self.connect(AnonymousUser())

        self.assertFalse(connected)

    async def test_non_participant_cannot_connect(self):
        """Test a user with no relation to the meeting cannot connect."""
        other_user = await sync_to_async(utils.create_user)(
            name="other", email="other@example.com"
        )

        communicator, connected = await self.connect(other_user)

        self.assertFalse(connected)

    async def test_pending_participant_cannot_connect(self):
        """Test a pending participant cannot connect."""
        participant = await sync_to_async(utils.create_user)(
            name="participant", email="participant@example.com"
        )
        await sync_to_async(utils.create_meeting_participant)(
            meeting=self.meeting, user=participant, invitation_status="PND"
        )

        communicator, connected = await self.connect(participant)

        self.assertFalse(connected)

    async def test_organizer_cannot_connect_when_room_inactive(self):
        """Test organizer cannot connect when the room is not active."""
        future_meeting = await sync_to_async(utils.create_meeting)(
            organizer=self.organizer,
            started_at=timezone.now() + timedelta(hours=2),
            ended_at=timezone.now() + timedelta(hours=3),
        )

        communicator, connected = await self.connect(
            self.organizer, meeting_id=future_meeting.id
        )

        self.assertFalse(connected)

    async def test_consumer_receives_room_message_event(self):
        """Test room message event is received from the room's channel group."""
        communicator, connected = await self.connect(self.organizer)
        self.assertTrue(connected)

        channel_layer = get_channel_layer()

        await channel_layer.group_send(
            f"room_{self.meeting.id}",
            {
                "type": "room.message",
                "kind": "room_message",
                "id": 5,
                "content": "Hello room!",
                "sender_id": self.organizer.id,
                "sender_name": self.organizer.name,
            },
        )

        response = await communicator.receive_json_from()

        self.assertEqual(
            response,
            {
                "kind": "room_message",
                "id": 5,
                "content": "Hello room!",
                "sender_id": self.organizer.id,
                "sender_name": self.organizer.name,
            },
        )

        await communicator.disconnect()
