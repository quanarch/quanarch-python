"""Thin calls: the quan says what to listen to, the quanar's api-manager listens."""

from __future__ import annotations

from .state import get_quanar_core
from .types import Handler


def get(path: str, handler: Handler) -> None:
    get_quanar_core().api.get(path, handler)


def post(path: str, handler: Handler) -> None:
    get_quanar_core().api.post(path, handler)


def put(path: str, handler: Handler) -> None:
    get_quanar_core().api.put(path, handler)


def patch(path: str, handler: Handler) -> None:
    get_quanar_core().api.patch(path, handler)


def delete(path: str, handler: Handler) -> None:
    get_quanar_core().api.delete(path, handler)
