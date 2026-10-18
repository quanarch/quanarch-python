"""Listens to a server-sent event stream: open, every named event, close."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

import httpx


async def follow(
    url: str,
    on_open: Callable[[], Awaitable[None]],
    on_event: Callable[[str], Awaitable[None]],
) -> None:
    """Returns when the stream ends or cannot be opened: the other side is gone."""
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=None)) as client:
            async with client.stream("GET", url, headers={"Accept": "text/event-stream"}) as response:
                if response.status_code != 200:
                    return
                await on_open()
                name = "message"
                async for line in response.aiter_lines():
                    if line.startswith("event:"):
                        name = line[6:].strip()
                    elif line == "":
                        await on_event(name)
                        name = "message"
    except (httpx.HTTPError, asyncio.CancelledError):
        return
