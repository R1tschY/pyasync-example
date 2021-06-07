#!/usr/bin/env python

from __future__ import annotations

import asyncio

from websockets import connect


async def main(url):
    async with connect(url) as websocket:
        print(await websocket.recv())
        await websocket.send("Hello")


if __name__ == '__main__':
    asyncio.run(main("ws://localhost:8765"))
