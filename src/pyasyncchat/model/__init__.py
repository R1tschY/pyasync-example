from __future__ import annotations

from typing import Literal, TypeVar

from pydantic import BaseModel, parse_raw_as

_eventTypes = []


class BaseEvent(BaseModel):
    type: str

    def __init_subclass__(cls, **kwargs):
        _eventTypes.append(cls)


# Receive

class HelloEvent(BaseEvent):
    type: Literal['hello'] = "hello"

    user_id: str


class MessageEvent(BaseEvent):
    type: Literal['message'] = "message"

    timestamp_ms: int
    user_id: str
    user_name: str
    message: str


class StatusEvent(BaseEvent):
    type: Literal['status'] = "status"

    timestamp_ms: int
    user_id: str
    user_name: str
    status_message: str


# Actions

class JoinRoomEvent(BaseEvent):
    type: Literal['join'] = "join"

    room_name: str


class SendMessageEvent(BaseEvent):
    type: Literal['send'] = "send"

    message: str


class ChangeNameEvent(BaseEvent):
    type: Literal['change_name'] = "change_name"

    new_name: str


Event = TypeVar("Event", *_eventTypes)


def parse_event(evt: str) -> Event:
    return parse_raw_as(Event, evt)


def dump_event(evt: Event) -> str:
    return evt.json()

