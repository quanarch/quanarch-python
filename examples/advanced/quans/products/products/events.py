"""What this quan does when other quans announce something."""

from __future__ import annotations

from typing import Any, cast

from shop_qua import EventMeta, EventSubscription

from .constants import Listens
from .services import stock
from .types import OrderEvent


async def _order_placed(payload: Any, _meta: EventMeta) -> None:
    await stock.reserve(cast(OrderEvent, payload))


async def _order_cancelled(payload: Any, _meta: EventMeta) -> None:
    await stock.release(cast(OrderEvent, payload))


order_events = [
    EventSubscription(Listens.ORDER_PLACED, _order_placed),
    EventSubscription(Listens.ORDER_CANCELLED, _order_cancelled),
]
