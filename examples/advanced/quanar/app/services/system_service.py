"""The quanar's own routes: its health, and what every quan declared. No business logic."""

from __future__ import annotations

import time

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ..constants import SystemRoute
from ..core import api_manager, event_manager, permission_manager, schema_manager
from . import quan_service

_started = time.monotonic()


async def health(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "uptime": round(time.monotonic() - _started)})


async def quans(_request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "quans": quan_service.status(),
            "apis": api_manager.describe(),
            "models": schema_manager.describe(),
            "permissions": permission_manager.all_permissions(),
            "events": event_manager.describe(),
        }
    )


routes = [Route(SystemRoute.HEALTH, health), Route(SystemRoute.QUANS, quans)]
