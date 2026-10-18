from __future__ import annotations

from typing import TypedDict

from .constants import Status


class OrderItem(TypedDict):
    product_id: str
    quantity: int


class OrderLine(OrderItem):
    name: str
    price: float


class Order(TypedDict):
    id: str
    user_id: str
    status: Status
    items: list[OrderItem]
    lines: list[OrderLine] | None
    total: float | None
    reason: str | None
    created_at: str
    updated_at: str


class ReservedEvent(TypedDict):
    """What products.reserved carries, as this quan reads it."""

    order_id: str
    total: float
    lines: list[OrderLine]


class RejectedEvent(TypedDict):
    order_id: str
    reason: str
