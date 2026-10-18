"""Take a request, return a response; only call services."""

from __future__ import annotations

from typing import cast

from shop_qua import ApiRequest, ApiResponse

from . import services
from .constants import Role
from .types import RegisterInput


async def register(req: ApiRequest) -> ApiResponse:
    return {"status": 201, "body": await services.register(cast(RegisterInput, req["body"]))}


async def login(req: ApiRequest) -> ApiResponse:
    return {"body": await services.login(req["body"]["email"], req["body"]["password"])}


async def me(req: ApiRequest) -> ApiResponse:
    assert req["user"] is not None
    return {"body": await services.me(req["user"]["id"])}


async def list_users(_req: ApiRequest) -> ApiResponse:
    return {"body": await services.list_users()}


async def set_role(req: ApiRequest) -> ApiResponse:
    assert req["user"] is not None
    return {"body": await services.set_role(req["params"]["id"], Role(req["body"]["role"]), req["user"]["id"])}
