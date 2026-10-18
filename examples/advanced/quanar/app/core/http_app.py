"""The quanar's HTTP server: its own routes, then whatever the quans asked it to listen to."""

from __future__ import annotations

import json
import time
import uuid
from http import HTTPStatus
from typing import Any

from shop_qua import ApiResponse
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.types import Lifespan

from ..config import settings
from ..constants import ErrorCode
from ..utils import HttpError, error_message
from . import api_manager, auth_manager
from .logger import get_logger
from .middleware_manager import RequestContext

log = get_logger("http")

#: Headers that stay with the quanar: a quan never sees the token.
_PRIVATE_HEADERS = {"authorization", "cookie"}


def _error(error: HttpError, request_id: str) -> Response:
    body: dict[str, Any] = {"code": error.code, "message": error.message}
    if error.details is not None:
        body["details"] = error.details
    return JSONResponse({"error": body, "request_id": request_id}, error.status)


def _answer(answer: ApiResponse) -> Response:
    status = answer.get("status", HTTPStatus.OK)
    if "body" not in answer:
        return Response(status_code=status, headers=answer.get("headers"))
    return JSONResponse(answer["body"], status, headers=answer.get("headers"))


async def _read_body(request: Request) -> Any:
    if int(request.headers.get("content-length") or 0) > settings.body_limit_bytes:
        raise HttpError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, ErrorCode.TOO_LARGE, "The body is too large")
    raw = await request.body()
    if len(raw) > settings.body_limit_bytes:
        raise HttpError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, ErrorCode.TOO_LARGE, "The body is too large")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        raise HttpError(HTTPStatus.BAD_REQUEST, ErrorCode.BAD_REQUEST, "The body is not valid JSON") from None


async def _dispatch(request: Request) -> Response:
    started = time.perf_counter()
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    authorization = request.headers.get("authorization", "")
    token = authorization[7:].strip() if authorization.lower().startswith("bearer ") else ""
    user = auth_manager.verify_token(token) if token else None
    method, path = request.method, request.url.path
    try:
        found = api_manager.find(method, path)
        if found is None:
            raise HttpError(HTTPStatus.NOT_FOUND, ErrorCode.NOT_FOUND, f"Nobody listens to {method} {path}")
        api, params = found
        ctx = RequestContext(
            request_id=request_id,
            user=user,
            client=request.client.host if request.client else "",
            method=method,
            path=path,
            params=params,
            query=dict(request.query_params),
            headers={k: v for k, v in request.headers.items() if k not in _PRIVATE_HEADERS},
            body=await _read_body(request),
        )
        response = _answer(await api_manager.handle(api, ctx))
    except HttpError as error:
        response = _error(error, request_id)
    except Exception as error:
        log.error(f"{method} {path} failed", error_message(error))
        response = _error(HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, ErrorCode.INTERNAL, "Internal error"), request_id)
    response.headers["x-request-id"] = request_id
    who = f" ({user['id'][:8]})" if user else ""
    log.info(f"{method} {request.url.path} → {response.status_code} {(time.perf_counter() - started) * 1000:.0f}ms{who}")
    return response


def create_app(system_routes: list[Route], lifespan: Lifespan[Starlette]) -> Starlette:
    catch_all = Route("/{path:path}", _dispatch, methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    return Starlette(routes=[*system_routes, catch_all], lifespan=lifespan)
