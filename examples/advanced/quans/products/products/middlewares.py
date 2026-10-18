"""The quan's own middlewares. They run in the quan, after the quanar's checks."""

from __future__ import annotations

from shop_qua import ApiRequest, ApiResponse, Next, Repository

from .constants import Model
from .errors import AppError
from .types import Product

_products: Repository[Product] = Repository(Model.PRODUCTS)


async def catch_errors(req: ApiRequest, next: Next) -> ApiResponse:  # noqa: A002
    """Turns the failures this quan expects into answers; anything else is the quanar's 500."""
    try:
        return await next()
    except AppError as error:
        return {"status": error.status, "body": {"error": {"code": error.code, "message": error.message}, "request_id": req["request_id"]}}


async def load_product(req: ApiRequest, next: Next) -> ApiResponse:  # noqa: A002
    """Finds the product of the path's {id} for the handler, or answers 404 before it runs."""
    product = await _products.find_by_id(req["params"]["id"])
    if product is None:
        return {"status": 404, "body": {"error": {"code": "product_not_found", "message": "No such product"}, "request_id": req["request_id"]}}
    req["locals"]["product"] = product
    return await next()
