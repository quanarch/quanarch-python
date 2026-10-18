from __future__ import annotations

from enum import StrEnum

QUAN_NAME = "products"

#: Below this many items, the quan says the stock is low.
LOW_STOCK = 5


class Route(StrEnum):
    LIST = "/products"
    ONE = "/products/{id}"
    RESTOCK = "/products/{id}/restock"


class Permission(StrEnum):
    MANAGE = "products:manage"


class Model(StrEnum):
    PRODUCTS = "products"
    RESERVATIONS = "reservations"


class Event(StrEnum):
    """Events this quan emits."""

    RESERVED = "products.reserved"
    REJECTED = "products.rejected"
    STOCK_LOW = "products.stock-low"


class Listens(StrEnum):
    """Events of other quans this quan listens to. It knows their names, never their code."""

    ORDER_PLACED = "orders.placed"
    ORDER_CANCELLED = "orders.cancelled"
