from __future__ import annotations

import logging
import time
from typing import Optional, Any
from weakref import WeakValueDictionary, WeakSet

from websockets.exceptions import ConnectionClosedError

from pyasyncchat.model import MessageEvent, StatusEvent, dump_event, HelloEvent, parse_event, SendMessageEvent, \
    JoinRoomEvent, ChangeNameEvent, Event


class ChatServer:
    logger = logging.getLogger(__name__)

    last_id = 0
    users: WeakSet[ChatUser]
    rooms: WeakValueDictionary[str, ChatRoom]
    lobby: ChatRoom

    def __init__(self):
        self.users = WeakSet()
        self.rooms = WeakValueDictionary()
        self.lobby = self.create_room("lobby")

    async def accept(self, websocket, path):
        self.logger.info(f"Accept connection {path}")

        self.last_id += 1

        user = ChatUser(str(self.last_id), "anonymous", self.lobby, websocket)
        await self.lobby.join_user(user)
        self.users.add(user)
        try:
            await user.run()
        finally:
            self.users.remove(user)

    def get_room(self, id: str) -> Optional[ChatRoom]:
        return self.rooms.get(id)

    def create_room(self, room_name: str):
        room = ChatRoom(room_name, self)
        self.rooms[room_name] = room
        return room


class ChatRoom:
    logger = logging.getLogger(__name__)

    name: str
    users: WeakSet[ChatUser]
    server: ChatServer

    def __init__(self, name: str, server: ChatServer):
        self.name = name
        self.users = WeakSet()
        self.server = server

    async def broadcast_message(self, user: ChatUser, message: str):
        await self._broadcast_event(MessageEvent(
            timestamp_ms=timestamp(),
            user_id=user.id,
            user_name=user.name,
            message=message
        ))

    async def broadcast_status_change(self, user: ChatUser, message: str):
        await self._broadcast_event(StatusEvent(
            timestamp_ms=timestamp(),
            user_id=user.id,
            user_name=user.name,
            status_message=message
        ))

    async def _broadcast_event(self, evt):
        for user in self.users:
            await user.send_event(evt)

    async def join_user(self, user: ChatUser):
        self.users.add(user)
        await self.broadcast_status_change(user, "joined room")

    async def leave_user(self, user: ChatUser):
        await self.broadcast_status_change(user, "left room")
        self.users.discard(user)

    async def notify_user_name_changed(self, user, old_name):
        await self.broadcast_status_change(
            user, f"changed name from {old_name} to {user.name}")


class ChatUser:
    logger = logging.getLogger(__name__)

    id: str
    name: str
    websocket: Any
    room: ChatRoom

    def __init__(self, id: str, name: str, room: ChatRoom, websocket: Any):
        self.id = id
        self.name = name
        self.websocket = websocket
        self.room = room

        self.logger.info("New user %s", id)

    async def run(self):
        ws = self.websocket

        await ws.send(dump_event(HelloEvent(user_id=self.id)))

        await self._receive()

    async def _receive(self):
        try:
            async for message in self.websocket:
                try:
                    evt = parse_event(message)
                except:
                    self.logger.error("ignored message: %s", message)
                    continue

                if isinstance(evt, SendMessageEvent):
                    await self.room.broadcast_message(self, evt.message)
                elif isinstance(evt, JoinRoomEvent):
                    room_name = evt.room_name
                    if room_name != self.room.name:
                        await self.join_room_by_name(room_name)
                elif isinstance(evt, ChangeNameEvent):
                    old_name = self.name
                    self.name = evt.new_name
                    await self.room.notify_user_name_changed(self, old_name)
                else:
                    self.logger.error("Unsupported message: %r", evt)
        except ConnectionClosedError:
            self.logger.error("User disconnected: %s", self.id)
            return

    async def send_event(self, evt: Event):
        await self.websocket.send(dump_event(evt))

    async def join_room_by_name(self, room_name: str):
        room = self.room.server.get_room(room_name)
        if not room:
            room = self.room.server.create_room(room_name)

        await self.join_room(room)

    async def join_room(self, room: ChatRoom):
        await self.room.leave_user(self)
        self.room = room
        await room.join_user(self)


def timestamp() -> int:
    return int(time.time() * 1000)
