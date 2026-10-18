"""Take a request, return a response; only call services."""

from __future__ import annotations

from typing import cast

from shop_qua import ApiRequest, ApiResponse

from .constants import Permission
from .services import products
from .types import NewProduct


async def list_products(req: ApiRequest) -> ApiResponse:
    query = req["query"]
    everything = req["user"] is not None and Permission.MANAGE in req["user"]["permissions"]
    found = await products.list_products(search=query.get("search"), limit=query.get("limit"), offset=query.get("offset"), everything=everything)
    return {"body": found}


async def get_product(req: ApiRequest) -> ApiResponse:
    return {"body": req["locals"]["product"]}


async def create_product(req: ApiRequest) -> ApiResponse:
    return {"status": 201, "body": await products.create(cast(NewProduct, req["body"]))}


async def update_product(req: ApiRequest) -> ApiResponse:
    return {"body": await products.update(req["params"]["id"], req["body"])}


async def restock_product(req: ApiRequest) -> ApiResponse:
    return {"body": await products.restock(req["params"]["id"], req["body"]["quantity"])}
