"""Orders never read the products' tables. An order is placed as pending and announced;
products answer with an event, and the order follows."""

from __future__ import annotations

from typing import Any

from shop_qua import AuthUser, Repository, events, log

from .constants import CANCELLABLE, Event, Model, Permission, Status
from .errors import AppError
from .types import Order, OrderItem, RejectedEvent, ReservedEvent

_orders: Repository[Order] = Repository(Model.ORDERS)


async def place(user_id: str, items: list[OrderItem]) -> Order:
    order = await _orders.create({"user_id": user_id, "status": Status.PENDING, "items": items})
    await events.emit(Event.PLACED, {"order_id": order["id"], "items": items})
    return order


async def list_orders(user: AuthUser, status: Status | None) -> list[Order]:
    where: dict[str, Any] = {} if Permission.READ_ALL in user["permissions"] else {"user_id": user["id"]}
    if status is not None:
        where["status"] = status
    return await _orders.find(where=where, order_by={"created_at": "desc"})


async def cancel(order: Order) -> Order:
    if order["status"] not in CANCELLABLE:
        raise AppError(409, "not_cancellable", f"A {order['status']} order cannot be cancelled")
    changed = await _orders.update({"id": order["id"], "status": {"in": CANCELLABLE}}, {"status": Status.CANCELLED})
    if changed == 0:
        raise AppError(409, "not_cancellable", "The order changed meanwhile, look again")
    await events.emit(Event.CANCELLED, {"order_id": order["id"], "items": order["items"]})
    cancelled = await _orders.find_by_id(order["id"])
    assert cancelled is not None
    return cancelled


async def confirm(event: ReservedEvent) -> None:
    order_id = event["order_id"]
    changed = await _orders.update(
        {"id": order_id, "status": Status.PENDING},
        {"status": Status.CONFIRMED, "total": event["total"], "lines": event["lines"]},
    )
    if changed == 0:
        # Cancelled before the stock was taken: give it back.
        await events.emit(Event.CANCELLED, {"order_id": order_id, "items": event["lines"]})
    else:
        log.info(f"order {order_id} confirmed, {event['total']}")


async def reject(event: RejectedEvent) -> None:
    await _orders.update({"id": event["order_id"], "status": Status.PENDING}, {"status": Status.REJECTED, "reason": event["reason"]})
