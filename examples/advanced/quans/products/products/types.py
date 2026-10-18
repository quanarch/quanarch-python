from __future__ import annotations

from typing import NotRequired, TypedDict


class Product(TypedDict):
    id: str
    name: str
    description: str | None
    price: float
    stock: int
    active: bool
    created_at: str
    updated_at: str


class NewProduct(TypedDict):
    name: str
    price: float
    description: NotRequired[str]
    stock: NotRequired[int]


class ReservedLine(TypedDict):
    product_id: str
    name: str
    price: float
    quantity: int


class Reservation(TypedDict):
    id: str
    order_id: str
    items: list[ReservedLine]
    total: float
    created_at: str
    updated_at: str


class OrderItem(TypedDict):
    product_id: str
    quantity: int


class OrderEvent(TypedDict):
    """What orders.placed and orders.cancelled carry, as this quan reads it."""

    order_id: str
    items: list[OrderItem]
