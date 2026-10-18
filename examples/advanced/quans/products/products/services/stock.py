"""Takes stock for orders and gives it back. Orders never touch this quan's tables: they say an
order was placed, and hear back whether it could be served."""

from __future__ import annotations

from shop_qua import DbOperation, Repository, db, events, log

from ..constants import LOW_STOCK, Event, Model
from ..types import OrderEvent, OrderItem, Product, Reservation, ReservedLine

_products: Repository[Product] = Repository(Model.PRODUCTS)
_reservations: Repository[Reservation] = Repository(Model.RESERVATIONS)


def _merge(items: list[OrderItem]) -> dict[str, int]:
    """The same product asked twice in one order is one line."""
    quantities: dict[str, int] = {}
    for item in items:
        quantities[item["product_id"]] = quantities.get(item["product_id"], 0) + item["quantity"]
    return quantities


async def reserve(order: OrderEvent) -> None:
    order_id = order["order_id"]
    if await _reservations.find_one({"order_id": order_id}):
        return

    async def reject(reason: str) -> None:
        await events.emit(Event.REJECTED, {"order_id": order_id, "reason": reason})

    wanted = _merge(order["items"])
    found = {p["id"]: p for p in await _products.find(where={"id": {"in": list(wanted)}, "active": True})}
    unknown = next((product_id for product_id in wanted if product_id not in found), None)
    if unknown is not None:
        return await reject(f"product {unknown} is not sold")

    lines: list[ReservedLine] = [
        {"product_id": product_id, "name": found[product_id]["name"], "price": found[product_id]["price"], "quantity": quantity}
        for product_id, quantity in wanted.items()
    ]
    total = round(sum(line["price"] * line["quantity"] for line in lines), 2)

    # Every line or none: an update that finds less stock than asked changes no row, and the batch rolls back.
    take: list[DbOperation] = [
        {
            "action": "update",
            "model": Model.PRODUCTS,
            "where": {"id": line["product_id"], "stock": {"gte": line["quantity"]}},
            "data": {"stock": {"decrement": line["quantity"]}},
            "expect": 1,
        }
        for line in lines
    ]
    create: DbOperation = {"action": "create", "model": Model.RESERVATIONS, "data": {"order_id": order_id, "items": lines, "total": total}}
    try:
        await db.transaction([*take, create])
    except RuntimeError:
        short = [line["name"] for line in lines if found[line["product_id"]]["stock"] < line["quantity"]]
        return await reject(f"not enough {', '.join(short)}" if short else "stock changed, try again")

    await events.emit(Event.RESERVED, {"order_id": order_id, "total": total, "lines": lines})
    for product in await _products.find(where={"id": {"in": [line["product_id"] for line in lines]}, "stock": {"lt": LOW_STOCK}}):
        await events.emit(Event.STOCK_LOW, {"product_id": product["id"], "name": product["name"], "stock": product["stock"]})


async def release(order: OrderEvent) -> None:
    order_id = order["order_id"]
    reservation = await _reservations.find_one({"order_id": order_id})
    if reservation is None:
        return
    give_back: list[DbOperation] = [
        {"action": "update", "model": Model.PRODUCTS, "where": {"id": line["product_id"]}, "data": {"stock": {"increment": line["quantity"]}}}
        for line in reservation["items"]
    ]
    await db.transaction([*give_back, {"action": "delete", "model": Model.RESERVATIONS, "where": {"order_id": order_id}, "expect": 1}])
    log.info(f"gave back the stock of order {order_id}")
