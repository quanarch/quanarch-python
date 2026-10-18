"""The quanar's middlewares. Quans name them; this is where a name becomes code, so a quan can
never bring its own authentication or skip a check."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from shop_qua import AuthUser, QuanarMiddleware

from ..config import settings
from ..constants import ErrorCode
from ..types import ValidationSpec
from ..utils import HttpError
from . import permission_manager, validation_manager


@dataclass
class RequestContext:
    """What the quanar knows about a request on its way to a quan."""

    request_id: str
    user: AuthUser | None
    client: str
    method: str
    path: str
    params: dict[str, Any]
    query: dict[str, Any]
    headers: dict[str, str]
    body: Any


#: One check before the quan: it returns, or raises the HttpError the client gets.
Step = Callable[[RequestContext], None]


def authenticate(ctx: RequestContext) -> None:
    if ctx.user is None:
        raise HttpError(HTTPStatus.UNAUTHORIZED, ErrorCode.UNAUTHENTICATED, "Sign in first")


def _rate_limit(key: str) -> Step:
    """A fixed window per client and api."""
    windows: dict[str, list[float]] = {}  # client → [start, count]

    def step(ctx: RequestContext) -> None:
        now = time.monotonic()
        window = windows.get(ctx.client)
        if window is None or now - window[0] > settings.rate_limit_window_seconds:
            windows[ctx.client] = [now, 1]
            return
        window[1] += 1
        if window[1] > settings.rate_limit_max:
            raise HttpError(HTTPStatus.TOO_MANY_REQUESTS, ErrorCode.RATE_LIMITED, "Too many requests, try again later")

    return step


def resolve(name: str, key: str) -> Step:
    match name:
        case QuanarMiddleware.AUTHENTICATE:
            return authenticate
        case QuanarMiddleware.RATE_LIMIT:
            return _rate_limit(key)
    raise ValueError(f'the quanar has no middleware "{name}"')


def permit(required: list[str]) -> list[Step]:
    def check(ctx: RequestContext) -> None:
        assert ctx.user is not None  # authenticate ran first
        missing = permission_manager.missing(ctx.user, required)
        if missing:
            raise HttpError(HTTPStatus.FORBIDDEN, ErrorCode.FORBIDDEN, f"Needs {', '.join(missing)}", {"missing": missing})

    return [authenticate, check]


def validate(rules: ValidationSpec) -> Step:
    def step(ctx: RequestContext) -> None:
        issues = validation_manager.validate(rules, ctx.params, ctx.query, ctx.body)
        if issues:
            raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, ErrorCode.VALIDATION, "The request is not valid", {"issues": issues})

    return step
