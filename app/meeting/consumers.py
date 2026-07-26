"""
Consumers for meeting app.
"""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from meeting.utils import user_accessible_room_meetings


class RoomConsumer(AsyncJsonWebsocketConsumer):
    """Handle real-time chat for a meeting's room."""

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

        self.group_name = f"room_{self.meeting_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Remove user connection from the room's group."""
        if hasattr(self, "group_name"):
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

        return meeting.room.is_active()

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
