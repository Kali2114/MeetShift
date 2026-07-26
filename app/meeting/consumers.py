"""
Consumers for meeting app.
"""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from core.models import Room
from meeting.utils import (
    mark_user_absent,
    mark_user_present,
    online_room_users,
    user_accessible_room_meetings,
)


class RoomConsumer(AsyncJsonWebsocketConsumer):
    """Handle real-time chat and presence for a meeting's room."""

    async def connect(self):
        """Connect user to their meeting room's group, if allowed."""
        user = self.scope["user"]
        self.meeting_id = self.scope["url_route"]["kwargs"]["meeting_id"]

        if not user.is_authenticated:
            await self.close()
            return

        allowed = await self.can_access_room(user)

        if not allowed:
            await self.close()
            return

        self.user = user
        self.group_name = f"room_{self.meeting_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        await self.mark_present()
        await self.broadcast_presence()

    async def disconnect(self, close_code):
        """Remove user connection from the room's group."""
        if hasattr(self, "group_name"):
            await self.mark_absent()
            await self.broadcast_presence()
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    @database_sync_to_async
    def can_access_room(self, user):
        """Return whether user can access this meeting's active room."""
        meeting = user_accessible_room_meetings(user).filter(id=self.meeting_id).first()

        if meeting is None:
            return False

        self.room_id = meeting.room.id

        return meeting.room.is_active()

    @database_sync_to_async
    def mark_present(self):
        """Record this connection as present in the room."""
        mark_user_present(Room.objects.get(id=self.room_id), self.user)

    @database_sync_to_async
    def mark_absent(self):
        """Remove this connection's presence in the room."""
        mark_user_absent(Room.objects.get(id=self.room_id), self.user)

    @database_sync_to_async
    def get_online_users_payload(self):
        """Return the current online users as JSON-serializable data."""
        room = Room.objects.get(id=self.room_id)
        return [{"id": user.id, "name": user.name} for user in online_room_users(room)]

    async def broadcast_presence(self):
        """Broadcast the current online users to the room's group."""
        online_users = await self.get_online_users_payload()

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "room.presence",
                "kind": "room_presence",
                "online_users": online_users,
            },
        )

    async def room_message(self, event):
        """Send room message data to browser."""
        await self.send_json(
            {
                "kind": event["kind"],
                "id": event["id"],
                "content": event["content"],
                "sender_id": event["sender_id"],
                "sender_name": event["sender_name"],
            }
        )

    async def room_presence(self, event):
        """Send presence update data to browser."""
        await self.send_json(
            {
                "kind": event["kind"],
                "online_users": event["online_users"],
            }
        )
