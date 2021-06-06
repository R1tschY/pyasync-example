#!/usr/bin/env python

from __future__ import annotations

import asyncio
from websockets import connect


async def hello(uri):
    async with connect(uri) as websocket:
        await websocket.send("Hello world!")
        print(await websocket.recv())

asyncio.run(hello("ws://localhost:8765"))
