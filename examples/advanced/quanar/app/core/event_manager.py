"""Carries events between quans. An emitter does not know who listens; a listener does not
know who emits. Delivery is at most once: a quan that is not mounted misses it."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from shop_qua import EventMeta

from ..utils import error_message, now_iso
from .logger import get_logger

log = get_logger("events")

Deliver = Callable[[int, Any, EventMeta], Awaitable[None]]

_listeners: dict[str, tuple[list[str], Deliver]] = {}
#: Deliveries on their way; kept so they are not collected mid-flight.
_flying: set[asyncio.Task[None]] = set()


def subscribe(owner: str, events: list[str], deliver: Deliver) -> None:
    _listeners[owner] = (events, deliver)


def forget(owner: str) -> None:
    _listeners.pop(owner, None)


async def _deliver(owner: str, event: str, deliver: Awaitable[None]) -> None:
    try:
        await deliver
    except Exception as error:
        log.error(f"{owner} failed on {event}", error_message(error))


def publish(emitted_by: str, event: str, payload: Any) -> int:
    """Returns how many subscriptions it reached."""
    if not event.startswith(f"{emitted_by}."):
        raise ValueError(f"{emitted_by} may not emit {event}: events start with {emitted_by}.")
    meta: EventMeta = {"emitted_by": emitted_by, "at": now_iso()}
    reached = 0
    for owner, (events, deliver) in _listeners.items():
        for subscription, name in enumerate(events):
            if name != event:
                continue
            reached += 1
            task = asyncio.create_task(_deliver(owner, event, deliver(subscription, payload, meta)))
            _flying.add(task)
            task.add_done_callback(_flying.discard)
    log.info(f"{event} from {emitted_by} → {reached} listener{'' if reached == 1 else 's'}")
    return reached


def describe() -> dict[str, list[str]]:
    return {owner: events for owner, (events, _) in _listeners.items()}
