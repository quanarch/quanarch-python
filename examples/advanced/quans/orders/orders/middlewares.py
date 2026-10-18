"""The quan's own middlewares. They run in the quan, after the quanar's checks."""

from __future__ import annotations

from shop_qua import ApiRequest, ApiResponse, Next, Repository

from .constants import Model, Permission
from .errors import AppError
from .types import Order

_orders: Repository[Order] = Repository(Model.ORDERS)


async def catch_errors(req: ApiRequest, next: Next) -> ApiResponse:  # noqa: A002
    """Turns the failures this quan expects into answers; anything else is the quanar's 500."""
    try:
        return await next()
    except AppError as error:
        return {"status": error.status, "body": {"error": {"code": error.code, "message": error.message}, "request_id": req["request_id"]}}


async def own_order(req: ApiRequest, next: Next) -> ApiResponse:  # noqa: A002
    """Loads the order of the path's {id} for the handler. Someone else's order answers 404,
    not 403: whether it exists is not told."""
    user = req["user"]
    assert user is not None  # the api requires a permission
    order = await _orders.find_by_id(req["params"]["id"])
    if order is None or (order["user_id"] != user["id"] and Permission.READ_ALL not in user["permissions"]):
        return {"status": 404, "body": {"error": {"code": "order_not_found", "message": "No such order"}, "request_id": req["request_id"]}}
    req["locals"]["order"] = order
    return await next()
