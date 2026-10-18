"""The quanar's own routes: its health and the state of its quans. No business logic."""

from __future__ import annotations

import time

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import quan_service

_started = time.monotonic()


async def health(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "uptime": round(time.monotonic() - _started)})


async def quans(_request: Request) -> JSONResponse:
    return JSONResponse(quan_service.status())


routes = [Route("/health", health), Route("/quans", quans)]
