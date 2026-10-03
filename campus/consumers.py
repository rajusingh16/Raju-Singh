import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class LocationConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = "campus_locations"

    async def connect(self):
        user = self.scope.get("user")
        # Requirement 6: Require login
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.user = user
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

        # Send initial confirmation and user's current room if any
        current_room_info = await self.get_user_current_room()
        await self.send(
            text_data=json.dumps(
                {
                    "event": "connected",
                    "user": self.user.username,
                    "email": self.user.email,
                    "current_room": current_room_info,
                    "message": "Connected to authenticated campus location updates.",
                }
            )
        )

    async def disconnect(self, close_code):
        if hasattr(self, "user") and self.user.is_authenticated:
            await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receives location update from a logged-in user:
        {
            "action": "update_location",
            "room_code": "GF_LIBRARY"
        }
        """
        try:
            payload = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"event": "error", "message": "Invalid JSON"}))
            return

        action = payload.get("action")
        if action == "update_location":
            room_code = payload.get("room_code")
            room_data = await self.set_user_room(room_code)
            if room_data:
                # Broadcast which room the person is in to the campus group
                await self.channel_layer.group_send(
                    self.GROUP_NAME,
                    {
                        "type": "location_broadcast",
                        "username": self.user.username,
                        "full_name": self.user.get_full_name() or self.user.username,
                        "role": getattr(self.user, "role", "STUDENT"),
                        "room_code": room_data["room_code"],
                        "room_name": room_data["name"],
                        "floor_level": room_data["floor_level"],
                        "timestamp": timezone.now().isoformat(),
                    },
                )
            else:
                await self.send(text_data=json.dumps({"event": "error", "message": "Room not found"}))
        else:
            await self.send(text_data=json.dumps({"event": "error", "message": "Unknown action"}))

    async def location_broadcast(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "event": "location_update",
                    "username": event["username"],
                    "full_name": event["full_name"],
                    "role": event["role"],
                    "room_code": event["room_code"],
                    "room_name": event["room_name"],
                    "floor_level": event["floor_level"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    @database_sync_to_async
    def get_user_current_room(self):
        if self.user.current_room:
            r = self.user.current_room
            return {
                "room_code": r.room_code,
                "name": r.name,
                "floor_level": r.floor.level,
            }
        return None

    @database_sync_to_async
    def set_user_room(self, room_code):
        from campus.models import Room
        try:
            room = Room.objects.select_related("floor").get(room_code=room_code)
            self.user.current_room = room
            self.user.last_seen_at = timezone.now()
            self.user.save(update_fields=["current_room", "last_seen_at"])
            return {
                "room_code": room.room_code,
                "name": room.name,
                "floor_level": room.floor.level,
            }
        except Room.DoesNotExist:
            return None
