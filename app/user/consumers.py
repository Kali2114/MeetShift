from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Handle real-time notifications for authenticated users."""

    async def connect(self):
        """Connect user to their personal notification group."""
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        self.group_name = f"notifications_user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Remove user connection from notification group."""
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def notification_message(self, event):
        """Send notification data to browser."""
        await self.send_json(
            {
                "id": event["id"],
                "message": event["message"],
                "meeting_id": event["meeting_id"],
                "unread_count": event["unread_count"],
            }
        )
