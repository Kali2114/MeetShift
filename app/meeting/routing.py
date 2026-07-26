from django.urls import path
from meeting.consumers import RoomConsumer

websocket_urlpatterns = [
    path("ws/room/<int:meeting_id>/", RoomConsumer.as_asgi()),
]
