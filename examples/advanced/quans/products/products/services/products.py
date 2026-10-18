"""The catalogue."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from shop_qua import Repository

from ..constants import Model
from ..errors import AppError
from ..types import NewProduct, Product

_products: Repository[Product] = Repository(Model.PRODUCTS)


async def list_products(*, search: str | None, limit: int | None, offset: int | None, everything: bool) -> list[Product]:
    """Active products for everyone; a manager may ask for the inactive ones too."""
    where: dict[str, Any] = {} if everything else {"active": True}
    if search:
        where["name"] = {"like": f"%{search}%"}
    return await _products.find(where=where, order_by={"name": "asc"}, limit=limit or 50, offset=offset or 0)


async def create(data: NewProduct) -> Product:
    if await _products.find_one({"name": data["name"]}):
        raise AppError(409, "name_taken", "A product with this name exists")
    return await _products.create(
        {"name": data["name"], "description": data.get("description"), "price": data["price"], "stock": data.get("stock", 0), "active": True}
    )


async def update(id: str, changes: Mapping[str, Any]) -> Product:  # noqa: A002
    product = await _products.update_by_id(id, changes)
    if product is None:
        raise AppError(404, "product_not_found", "No such product")
    return product


async def restock(id: str, quantity: int) -> Product:  # noqa: A002
    return await update(id, {"stock": {"increment": quantity}})
