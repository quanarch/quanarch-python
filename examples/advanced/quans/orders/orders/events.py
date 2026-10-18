"""What this quan does when products answer."""

from __future__ import annotations

from typing import Any, cast

from shop_qua import EventMeta, EventSubscription

from . import services
from .constants import Listens
from .types import RejectedEvent, ReservedEvent


async def _reserved(payload: Any, _meta: EventMeta) -> None:
    await services.confirm(cast(ReservedEvent, payload))


async def _rejected(payload: Any, _meta: EventMeta) -> None:
    await services.reject(cast(RejectedEvent, payload))


product_events = [
    EventSubscription(Listens.RESERVED, _reserved),
    EventSubscription(Listens.REJECTED, _rejected),
]
