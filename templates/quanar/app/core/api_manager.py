"""The quanar's listener table: quans ask it, through the qua, to listen to a method and a path."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from starlette.routing import Match, Route

Forward = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


@dataclass
class Listener:
    owner: str
    method: str
    path: str
    route: Route
    forward: Forward


_listeners: list[Listener] = []


def normalize(path: str) -> str:
    """"items" or "/items/" -> "/items" """
    return "/" + path.strip("/")


def listen(owner: str, method: str, path: str, forward: Forward) -> None:
    path = normalize(path)
    # Starlette parses the path pattern; the endpoint is never called directly.
    route = Route(path, endpoint=lambda request: None, methods=[method])
    _listeners.append(Listener(owner, method, path, route, forward))


def forget(owner: str) -> None:
    """Stops listening to everything a quan asked for."""
    _listeners[:] = [l for l in _listeners if l.owner != owner]


def find(method: str, path: str) -> tuple[Listener, dict[str, str]] | None:
    scope = {"type": "http", "method": method, "path": path}
    for listener in _listeners:
        match, child = listener.route.matches(scope)
        if match is Match.FULL:
            return listener, {k: str(v) for k, v in child.get("path_params", {}).items()}
    return None


def listening(owner: str) -> list[str]:
    return [f"{l.method} {l.path}" for l in _listeners if l.owner == owner]
