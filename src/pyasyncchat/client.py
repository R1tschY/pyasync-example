import asyncio
from threading import Thread
from typing import Optional

from websockets import connect

from pyasyncchat.model import BaseEvent, dump_event, parse_event, ChangeNameEvent, JoinRoomEvent, SendMessageEvent, \
    MessageEvent, StatusEvent


class EventDispatcher:

    def __init__(self, websocket):
        self.websocket = websocket

    async def send_event(self, event: BaseEvent):
        await self.websocket.send(dump_event(event))

    async def recv_event(self) -> BaseEvent:
        return parse_event(await self.websocket.recv())


class ConsoleInput:

    def __init__(self):
        self.thread = Thread(target=self.prompt, name="prompt", daemon=True)
        self.thread.start()
        self.loop = asyncio.get_event_loop()
        self.input_queue = asyncio.Queue()

    def prompt(self):
        while True:
            s = input("")
            self.loop.call_soon_threadsafe(self.input_queue.put_nowait, s)

    async def recv(self) -> Optional[str]:
        return await self.input_queue.get()


class Chat:

    def __init__(self, dispatcher: EventDispatcher):
        self.dispatcher = dispatcher
        self.room = "lobby"

    async def run(self):
        pass

    async def consume_input(self, console_input: ConsoleInput):
        while True:
            s = await console_input.recv()
            if s.rstrip() == "/quit":
                return
            elif s.startswith("/rename "):
                await self.dispatcher.send_event(ChangeNameEvent(new_name=s.split(maxsplit=1)[1].strip()))
            elif s.startswith("/join "):
                await self.dispatcher.send_event(JoinRoomEvent(room_name=s.split(maxsplit=1)[1].strip()))
            else:
                await self.dispatcher.send_event(SendMessageEvent(message=s))

    async def consume_events(self, dispatcher: EventDispatcher):
        while True:
            evt = await dispatcher.recv_event()
            if evt is None:
                return

            if isinstance(evt, MessageEvent):
                print(f"{evt.user_name}: {evt.message}")
            elif isinstance(evt, StatusEvent):
                print(f"*{evt.user_name} {evt.status_message}*")


async def main(url):
    async with connect(url) as websocket:
        dispatcher = EventDispatcher(websocket)
        chat = Chat(dispatcher)
        console_input = ConsoleInput()

        input_task = asyncio.ensure_future(chat.consume_input(console_input))
        output_task = asyncio.ensure_future(chat.consume_events(dispatcher))

        done, pending = await asyncio.wait(
            [input_task, output_task],
            return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()


if __name__ == '__main__':
    asyncio.run(main("ws://localhost:8765"))
