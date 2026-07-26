"""
Tests for meeting consumers.
"""

from datetime import timedelta

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from core.metrics import (
    websocket_connections_active,
    websocket_connections_total,
    websocket_disconnections_total,
)
from core.models import RoomPresence
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

    async def test_connect_and_disconnect_update_websocket_metrics(self):
        """Test connecting/disconnecting updates the WebSocket connection metrics."""
        active = websocket_connections_active.labels(consumer="room")
        total = websocket_connections_total.labels(consumer="room")
        disconnections = websocket_disconnections_total.labels(consumer="room")

        active_before = active._value.get()
        total_before = total._value.get()
        disconnections_before = disconnections._value.get()

        communicator, connected = await self.connect(self.organizer)
        self.assertTrue(connected)
        await communicator.receive_json_from()  # organizer's own join broadcast

        self.assertEqual(active._value.get(), active_before + 1)
        self.assertEqual(total._value.get(), total_before + 1)

        await communicator.disconnect()

        self.assertEqual(active._value.get(), active_before)
        self.assertEqual(disconnections._value.get(), disconnections_before + 1)

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

    async def test_connect_marks_user_present_and_broadcasts(self):
        """Test connecting creates a presence row and broadcasts the online list."""
        communicator, connected = await self.connect(self.organizer)
        self.assertTrue(connected)

        response = await communicator.receive_json_from()

        self.assertEqual(response["kind"], "room_presence")
        self.assertEqual(
            response["online_users"],
            [{"id": self.organizer.id, "name": self.organizer.name}],
        )

        presence_exists = await sync_to_async(
            RoomPresence.objects.filter(
                room=self.meeting.room, user=self.organizer
            ).exists
        )()
        self.assertTrue(presence_exists)

        await communicator.disconnect()

    async def test_disconnect_marks_user_absent_and_broadcasts(self):
        """Test disconnecting removes the presence row and broadcasts the update."""
        participant = await sync_to_async(utils.create_user)(
            name="participant", email="participant@example.com"
        )
        await sync_to_async(utils.create_meeting_participant)(
            meeting=self.meeting, user=participant, invitation_status="ACC"
        )

        communicator, connected = await self.connect(self.organizer)
        self.assertTrue(connected)
        await communicator.receive_json_from()  # organizer's own join broadcast

        second_communicator, second_connected = await self.connect(participant)
        self.assertTrue(second_connected)

        await communicator.receive_json_from()  # organizer sees participant join
        await second_communicator.receive_json_from()  # participant's own join

        await communicator.disconnect()

        response = await second_communicator.receive_json_from()

        self.assertEqual(response["kind"], "room_presence")
        self.assertEqual(len(response["online_users"]), 1)
        self.assertEqual(response["online_users"][0]["id"], participant.id)

    async def test_same_user_two_tabs_stays_online_until_both_disconnect(self):
        """Test one of two tabs for the same user closing keeps them online."""
        first, first_connected = await self.connect(self.organizer)
        self.assertTrue(first_connected)
        await first.receive_json_from()  # first tab's own join broadcast

        second, second_connected = await self.connect(self.organizer)
        self.assertTrue(second_connected)
        await first.receive_json_from()  # first tab sees the second tab join
        await second.receive_json_from()  # second tab's own join broadcast

        await first.disconnect()

        response = await second.receive_json_from()

        self.assertEqual(response["kind"], "room_presence")
        self.assertEqual(
            response["online_users"],
            [{"id": self.organizer.id, "name": self.organizer.name}],
        )

        presence = await sync_to_async(RoomPresence.objects.get)(
            room=self.meeting.room, user=self.organizer
        )
        self.assertEqual(presence.connection_count, 1)

        await second.disconnect()

        presence_exists = await sync_to_async(
            RoomPresence.objects.filter(
                room=self.meeting.room, user=self.organizer
            ).exists
        )()
        self.assertFalse(presence_exists)

    async def test_reconnect_cycle_does_not_leak_presence_or_metrics(self):
        """Test a disconnect/reconnect cycle returns cleanly to baseline state."""
        active = websocket_connections_active.labels(consumer="room")
        active_before = active._value.get()

        communicator, connected = await self.connect(self.organizer)
        self.assertTrue(connected)
        await communicator.receive_json_from()  # own join broadcast
        await communicator.disconnect()

        self.assertEqual(active._value.get(), active_before)
        presence_exists = await sync_to_async(
            RoomPresence.objects.filter(
                room=self.meeting.room, user=self.organizer
            ).exists
        )()
        self.assertFalse(presence_exists)

        # Simulates ws-reconnect.js firing a fresh connect() after the close event.
        reconnected, reconnected_ok = await self.connect(self.organizer)
        self.assertTrue(reconnected_ok)
        await reconnected.receive_json_from()  # own join broadcast

        self.assertEqual(active._value.get(), active_before + 1)

        presence = await sync_to_async(RoomPresence.objects.get)(
            room=self.meeting.room, user=self.organizer
        )
        self.assertEqual(presence.connection_count, 1)

        await reconnected.disconnect()
