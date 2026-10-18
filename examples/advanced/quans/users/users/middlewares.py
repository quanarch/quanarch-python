"""The quan's own middlewares. They run in the quan, after the quanar's checks."""

from __future__ import annotations

from shop_qua import ApiRequest, ApiResponse, Next, log

from .errors import AppError


async def catch_errors(req: ApiRequest, next: Next) -> ApiResponse:  # noqa: A002
    """Turns the failures this quan expects into answers; anything else is the quanar's 500."""
    try:
        return await next()
    except AppError as error:
        return {"status": error.status, "body": {"error": {"code": error.code, "message": error.message}, "request_id": req["request_id"]}}


async def audit(req: ApiRequest, next: Next) -> ApiResponse:  # noqa: A002
    """Writes down who changed what, after the change went through."""
    res = await next()
    if res.get("status", 200) < 400:
        who = req["user"]["name"] if req["user"] else "someone"
        log.info(f"{who} {req['method']} {req['path']}", req["body"])
    return res
