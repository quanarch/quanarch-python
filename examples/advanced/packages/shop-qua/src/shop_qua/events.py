"""A quan announces what happened; the quanar carries it to whoever listens."""

from __future__ import annotations

from typing import Any

from .state import get_quanar_core


async def emit(event: str, payload: Any) -> None:
    """The name must start with the quan's name: orders.placed"""
    await get_quanar_core().events.emit(event, payload)
