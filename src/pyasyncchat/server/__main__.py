#!/usr/bin/env python

from __future__ import annotations

import asyncio
import logging
import os

import websockets

from pyasyncchat.server import ChatServer

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level="DEBUG")

    port = os.environ.get("CHAT_SERVER_LISTEN_PORT", 8765)

    server = ChatServer()

    start_server = websockets.serve(server.accept, "localhost", port)
    logger.info("Listing on localhost:%d ...", port)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()


if __name__ == '__main__':
    main()
