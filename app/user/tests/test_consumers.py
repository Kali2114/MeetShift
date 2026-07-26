from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from core.metrics import (
    websocket_connections_active,
    websocket_connections_total,
    websocket_disconnections_total,
)
from core.tests import utils
from django.test import TransactionTestCase, override_settings
from user.routing import websocket_urlpatterns

TEST_CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
class NotificationConsumerTests(TransactionTestCase):
    """Tests for notification WebSocket consumer."""

    def setUp(self):
        """Create user for tests."""
        self.user = utils.create_user()

    async def test_authenticated_user_can_connect(self):
        """Test authenticated user can connect to notification WebSocket."""
        application = URLRouter(websocket_urlpatterns)

        communicator = WebsocketCommunicator(
            application,
            "/ws/notifications/",
        )
        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_anonymous_user_cannot_connect(self):
        """Test anonymous user cannot connect to notification WebSocket."""
        from django.contrib.auth.models import AnonymousUser

        application = URLRouter(websocket_urlpatterns)

        communicator = WebsocketCommunicator(
            application,
            "/ws/notifications/",
        )
        communicator.scope["user"] = AnonymousUser()

        connected, _ = await communicator.connect()

        self.assertFalse(connected)

    async def test_consumer_receives_event_from_user_group(self):
        """Test notification event is received from user's channel group."""
        application = URLRouter(websocket_urlpatterns)

        communicator = WebsocketCommunicator(
            application,
            "/ws/notifications/",
        )
        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        channel_layer = get_channel_layer()

        await channel_layer.group_send(
            f"notifications_user_{self.user.id}",
            {
                "type": "notification.message",
                "id": 12,
                "message": "You have been invited.",
                "meeting_id": 4,
                "conversation_id": None,
                "unread_count": 2,
            },
        )

        response = await communicator.receive_json_from()

        self.assertEqual(
            response,
            {
                "id": 12,
                "message": "You have been invited.",
                "meeting_id": 4,
                "conversation_id": None,
                "unread_count": 2,
            },
        )

        await communicator.disconnect()

    async def test_connect_and_disconnect_update_websocket_metrics(self):
        """Test connecting/disconnecting updates the WebSocket connection metrics."""
        active = websocket_connections_active.labels(consumer="notifications")
        total = websocket_connections_total.labels(consumer="notifications")
        disconnections = websocket_disconnections_total.labels(consumer="notifications")

        active_before = active._value.get()
        total_before = total._value.get()
        disconnections_before = disconnections._value.get()

        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(application, "/ws/notifications/")
        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        self.assertEqual(active._value.get(), active_before + 1)
        self.assertEqual(total._value.get(), total_before + 1)

        await communicator.disconnect()

        self.assertEqual(active._value.get(), active_before)
        self.assertEqual(disconnections._value.get(), disconnections_before + 1)

    async def test_consumer_receives_conversation_update_event(self):
        """Test conversation update event is received from user's channel group."""
        application = URLRouter(websocket_urlpatterns)

        communicator = WebsocketCommunicator(
            application,
            "/ws/notifications/",
        )
        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        channel_layer = get_channel_layer()

        await channel_layer.group_send(
            f"notifications_user_{self.user.id}",
            {
                "type": "conversation.update",
                "kind": "conversation_update",
                "id": 42,
                "conversation_id": 7,
                "message": "Hello!",
                "sender_name": "Sender",
                "unread_count": 1,
                "total_unread_count": 3,
            },
        )

        response = await communicator.receive_json_from()

        self.assertEqual(
            response,
            {
                "kind": "conversation_update",
                "id": 42,
                "conversation_id": 7,
                "message": "Hello!",
                "sender_name": "Sender",
                "unread_count": 1,
                "total_unread_count": 3,
            },
        )

        await communicator.disconnect()
