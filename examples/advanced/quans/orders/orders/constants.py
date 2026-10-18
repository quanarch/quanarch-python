from __future__ import annotations

from enum import StrEnum

QUAN_NAME = "orders"


class Route(StrEnum):
    LIST = "/orders"
    ONE = "/orders/{id}"
    CANCEL = "/orders/{id}/cancel"


class Permission(StrEnum):
    CREATE = "orders:create"
    READ = "orders:read"
    READ_ALL = "orders:read-all"


class Model(StrEnum):
    ORDERS = "orders"


class Status(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


#: An order can be cancelled until it is closed.
CANCELLABLE = [Status.PENDING, Status.CONFIRMED]


class Event(StrEnum):
    """Events this quan emits."""

    PLACED = "orders.placed"
    CANCELLED = "orders.cancelled"


class Listens(StrEnum):
    """Events of other quans this quan listens to."""

    RESERVED = "products.reserved"
    REJECTED = "products.rejected"
