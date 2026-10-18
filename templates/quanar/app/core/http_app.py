"""The quanar's HTTP server: its own routes, then whatever the quans asked it to listen to."""

from __future__ import annotations

import json
import time

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.types import Lifespan

from . import api_manager
from .logger import get_logger

log = get_logger("http")


async def _dispatch(request: Request) -> Response:
    started = time.perf_counter()
    found = api_manager.find(request.method, request.url.path)
    if found is None:
        response: Response = JSONResponse({"error": f"Nobody listens to {request.method} {request.url.path}"}, 404)
    else:
        listener, params = found
        raw = await request.body()
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return JSONResponse({"error": "The body is not valid JSON"}, 400)
        answer = await listener.forward(
            {
                "method": request.method,
                "path": request.url.path,
                "params": params,
                "query": dict(request.query_params),
                "headers": {k: v for k, v in request.headers.items() if k not in ("authorization", "cookie")},
                "body": body,
            }
        )
        status = answer.get("status", 200)
        response = Response(status_code=status) if "body" not in answer else JSONResponse(answer["body"], status)
    log.info("%s %s → %s %.0fms", request.method, request.url.path, response.status_code, (time.perf_counter() - started) * 1000)
    return response


def create_app(system_routes: list[Route], lifespan: Lifespan[Starlette]) -> Starlette:
    catch_all = Route("/{path:path}", _dispatch, methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    return Starlette(routes=[*system_routes, catch_all], lifespan=lifespan)
