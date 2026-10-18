"""Thin calls: the quan names the table, the quanar's db-manager stores."""

from __future__ import annotations

import builtins
from typing import Any

from .state import get_quanar_core
from .types import Row


async def create(table: str, data: dict[str, Any]) -> Row:
    return await get_quanar_core().db.create(table, data)


async def list(table: str) -> builtins.list[Row]:  # noqa: A001 - mirrors the quanar's method
    return await get_quanar_core().db.list(table)


async def get(table: str, id: str) -> Row | None:  # noqa: A002
    return await get_quanar_core().db.get(table, id)


async def update(table: str, id: str, data: dict[str, Any]) -> Row | None:  # noqa: A002
    return await get_quanar_core().db.update(table, id, data)


async def remove(table: str, id: str) -> bool:  # noqa: A002
    return await get_quanar_core().db.remove(table, id)
