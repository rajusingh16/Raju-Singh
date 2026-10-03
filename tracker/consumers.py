import asyncio
import json
import math
import secrets
from datetime import datetime, timedelta, timezone

from channels.generic.websocket import AsyncWebsocketConsumer


# Academic-demo registry. Shares are deliberately memory-only and disappear on restart.
ACTIVE_SHARES = {}


def _now():
    return datetime.now(timezone.utc)


class CampusTrackerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.joined_groups = set()
        self.owned_token = None
        self.expiry_task = None
        await self.accept()
        await self._send("connected", message="Private live tracking is ready.")

    async def disconnect(self, close_code):
        if self.expiry_task:
            self.expiry_task.cancel()
            self.expiry_task = None
        for group in self.joined_groups:
            await self.channel_layer.group_discard(group, self.channel_name)
        if self.owned_token and self.owned_token in ACTIVE_SHARES:
            share = ACTIVE_SHARES.pop(self.owned_token)
            await self.channel_layer.group_send(
                share["group"], {"type": "share_ended", "reason": "Owner disconnected."}
            )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            await self._send("error", message="Invalid tracking message.")
            return

        action = data.get("action")
        if action == "start_share":
            await self._start_share(data)
        elif action == "join_share":
            await self._join_share(data)
        elif action == "position_update":
            await self._position_update(data)
        elif action == "stop_share":
            await self._stop_share()
        else:
            await self._send("error", message="Unknown tracking action.")

    async def _start_share(self, data):
        if data.get("consent") is not True:
            await self._send("error", message="Explicit consent is required to share location.")
            return

        try:
            minutes = int(data.get("duration", 15))
        except (TypeError, ValueError):
            minutes = 15
        minutes = minutes if minutes in (15, 30, 60) else 15
        if self.owned_token:
            await self._stop_share(notify=False)

        token = secrets.token_hex(3).upper()
        while token in ACTIVE_SHARES:
            token = secrets.token_hex(3).upper()
        group = f"share_{token.lower()}"
        expiry = _now() + timedelta(minutes=minutes)
        display_name = str(data.get("display_name") or "").strip()[:60] or "Campus visitor"
        ACTIVE_SHARES[token] = {
            "owner_channel": self.channel_name,
            "display_name": display_name,
            "expires_at": expiry,
            "group": group,
        }
        self.owned_token = token
        self.joined_groups.add(group)
        await self.channel_layer.group_add(group, self.channel_name)
        self.expiry_task = asyncio.create_task(self._expire_share(token, minutes * 60))
        await self._send(
            "share_started",
            token=token,
            expires_at=expiry.isoformat(),
            message="Share this private code only with an approved person.",
        )

    async def _join_share(self, data):
        token = str(data.get("token") or "").strip().upper()
        share = ACTIVE_SHARES.get(token)
        if not share:
            await self._send("error", message="That share code is invalid or has expired.")
            return
        group = share["group"]
        self.joined_groups.add(group)
        await self.channel_layer.group_add(group, self.channel_name)
        await self._send(
            "share_joined",
            token=token,
            display_name=share["display_name"],
            expires_at=share["expires_at"].isoformat(),
        )

    async def _position_update(self, data):
        share = ACTIVE_SHARES.get(self.owned_token)
        if not share or share["owner_channel"] != self.channel_name:
            await self._send("error", message="Start a private share before sending a position.")
            return
        point_code = str(data.get("point_code") or "").strip()[:60]
        if not point_code:
            await self._send("error", message="A valid campus point is required.")
            return
        try:
            floor = int(data.get("floor", 0))
            coordinates = tuple(float(data.get(axis, 0)) for axis in ("x", "y", "z"))
        except (TypeError, ValueError):
            await self._send("error", message="Location coordinates must be numeric.")
            return
        if not all(math.isfinite(value) for value in coordinates):
            await self._send("error", message="Location coordinates must be finite numbers.")
            return
        x, y, z = coordinates
        payload = {
            "type": "position_message",
            "display_name": share["display_name"],
            "point_code": point_code,
            "room_name": str(data.get("room_name") or "")[:120],
            "floor": floor,
            "x": x,
            "y": y,
            "z": z,
            "updated_at": _now().isoformat(),
        }
        await self.channel_layer.group_send(share["group"], payload)

    async def _stop_share(self, notify=True):
        if self.expiry_task and self.expiry_task is not asyncio.current_task():
            self.expiry_task.cancel()
        self.expiry_task = None
        share = ACTIVE_SHARES.pop(self.owned_token, None)
        self.owned_token = None
        if share:
            await self.channel_layer.group_send(
                share["group"], {"type": "share_ended", "reason": "Location sharing stopped."}
            )
        if notify:
            await self._send("share_stopped")

    async def _expire_share(self, token, delay_seconds):
        try:
            await asyncio.sleep(delay_seconds)
        except asyncio.CancelledError:
            return
        share = ACTIVE_SHARES.pop(token, None)
        if not share or self.owned_token != token:
            return
        self.owned_token = None
        self.expiry_task = None
        await self.channel_layer.group_send(
            share["group"], {"type": "share_ended", "reason": "Location share expired."}
        )

    async def position_message(self, event):
        await self._send(
            "position_update",
            display_name=event["display_name"],
            point_code=event["point_code"],
            room_name=event["room_name"],
            floor=event["floor"],
            x=event["x"],
            y=event["y"],
            z=event["z"],
            updated_at=event["updated_at"],
        )

    async def share_ended(self, event):
        await self._send("share_ended", reason=event["reason"])

    async def _send(self, event, **payload):
        await self.send(text_data=json.dumps({"event": event, **payload}))
