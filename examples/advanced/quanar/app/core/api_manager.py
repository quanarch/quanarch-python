"""Opens the apis quans declare. For each api, in one pass: the quanar's middlewares, then
authentication and permissions, then validation, and only then the quan. Removing a quan
closes its apis at once."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from shop_qua import ApiRequest, ApiResponse, QuanarMiddleware
from starlette.routing import Match, Route

from ..types import ApiMeta
from . import middleware_manager
from .middleware_manager import RequestContext, Step

Invoke = Callable[[int, ApiRequest], Awaitable[ApiResponse]]


@dataclass
class OpenApi:
    owner: str
    index: int
    meta: ApiMeta
    #: Starlette reads the endpoint's pattern, /products/{id}; it is never called.
    route: Route
    steps: list[Step]
    invoke: Invoke


_open: dict[str, list[OpenApi]] = {}


def _unused(_request: Any) -> None:
    return None


def create(owner: str, apis: list[ApiMeta], invoke: Invoke) -> None:
    opened: list[OpenApi] = []
    for index, api in enumerate(apis):
        endpoint = api["endpoint"]
        if endpoint != f"/{owner}" and not endpoint.startswith(f"/{owner}/"):
            raise ValueError(f"{owner} may not listen to {endpoint}: endpoints start with /{owner}")
        key = f"{api['method']} {endpoint}"
        permissions = api["permissions"]
        steps = [
            middleware_manager.resolve(m, key)
            for m in api["middlewares"]
            # Permissions authenticate on their own.
            if not (permissions and m == QuanarMiddleware.AUTHENTICATE)
        ]
        if permissions:
            steps += middleware_manager.permit(permissions)
        if api["validation"]:
            steps.append(middleware_manager.validate(api["validation"]))
        opened.append(OpenApi(owner, index, api, Route(endpoint, _unused, methods=[api["method"]]), steps, invoke))
    _open[owner] = opened


def remove(owner: str) -> None:
    _open.pop(owner, None)


def find(method: str, path: str) -> tuple[OpenApi, dict[str, str]] | None:
    scope = {"type": "http", "method": method, "path": path}
    for apis in _open.values():
        for api in apis:
            match, child = api.route.matches(scope)
            if match is Match.FULL:
                return api, {k: str(v) for k, v in child.get("path_params", {}).items()}
    return None


async def handle(api: OpenApi, ctx: RequestContext) -> ApiResponse:
    for step in api.steps:
        step(ctx)
    request: ApiRequest = {
        "request_id": ctx.request_id,
        "method": ctx.method,
        "path": ctx.path,
        "params": ctx.params,
        "query": ctx.query,
        "headers": ctx.headers,
        "body": ctx.body,
        "user": ctx.user,
        "locals": {},
    }
    return await api.invoke(api.index, request)


def describe() -> dict[str, list[dict[str, Any]]]:
    return {
        owner: [
            {
                "method": a.meta["method"],
                "endpoint": a.meta["endpoint"],
                "permissions": a.meta["permissions"],
                "middlewares": a.meta["middlewares"],
                "validated": a.meta["validation"] is not None,
                "description": a.meta["description"],
            }
            for a in apis
        ]
        for owner, apis in _open.items()
    }
