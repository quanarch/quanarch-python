"""Take a request, return a response; only call services."""

from __future__ import annotations

from shop_qua import ApiRequest, ApiResponse

from . import services
from .constants import Status


async def place_order(req: ApiRequest) -> ApiResponse:
    """202: the order is taken, its fate is decided when products answer."""
    assert req["user"] is not None
    return {"status": 202, "body": await services.place(req["user"]["id"], req["body"]["items"])}


async def list_orders(req: ApiRequest) -> ApiResponse:
    assert req["user"] is not None
    status = req["query"].get("status")
    return {"body": await services.list_orders(req["user"], Status(status) if status else None)}


async def get_order(req: ApiRequest) -> ApiResponse:
    return {"body": req["locals"]["order"]}


async def cancel_order(req: ApiRequest) -> ApiResponse:
    return {"body": await services.cancel(req["locals"]["order"])}
