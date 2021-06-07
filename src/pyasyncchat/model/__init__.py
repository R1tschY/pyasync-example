from __future__ import annotations

from typing import TypeVar, ClassVar

from pydantic import BaseModel, parse_raw_as, validator

_eventTypes = []


class BaseEvent(BaseModel):
    TYPE_NAME: ClassVar[str] = None
    type: str

    def __init_subclass__(cls, **kwargs):
        _eventTypes.append(cls)

    @validator('type')
    def type_match(cls, v):
        if v != cls.TYPE_NAME:
            raise ValueError('type does not match')
        return v


# Receive

class HelloEvent(BaseEvent):
    TYPE_NAME = "hello"
    type = TYPE_NAME

    user_id: str


class MessageEvent(BaseEvent):
    TYPE_NAME = "message"
    type = TYPE_NAME

    timestamp_ms: int
    user_id: str
    user_name: str
    message: str


class StatusEvent(BaseEvent):
    TYPE_NAME = "status"
    type = TYPE_NAME

    timestamp_ms: int
    user_id: str
    user_name: str
    status_message: str


# Actions

class JoinRoomEvent(BaseEvent):
    TYPE_NAME = "join"
    type = TYPE_NAME

    room_name: str


class SendMessageEvent(BaseEvent):
    TYPE_NAME = "send"
    type = TYPE_NAME

    message: str


class ChangeNameEvent(BaseEvent):
    TYPE_NAME = "change_name"
    type = TYPE_NAME

    new_name: str


Event = TypeVar("Event", *_eventTypes)


def parse_event(evt: str) -> Event:
    return parse_raw_as(Event, evt)


def dump_event(evt: Event) -> str:
    return evt.json()

