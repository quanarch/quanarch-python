"""The quanar's database. It knows no tables in advance: the quan names them."""

from __future__ import annotations

import builtins
import uuid
from typing import Any

Row = dict[str, Any]

# table -> id -> row. Kept in memory; replace this module to use a real database.
_tables: dict[str, dict[str, Row]] = {}


def _table(name: str) -> dict[str, Row]:
    return _tables.setdefault(name, {})


async def create(table: str, data: dict[str, Any]) -> Row:
    row = {**data, "id": str(uuid.uuid4())}
    _table(table)[row["id"]] = row
    return row


async def list(table: str) -> builtins.list[Row]:  # noqa: A001
    return [*_table(table).values()]


async def get(table: str, id: str) -> Row | None:  # noqa: A002
    return _table(table).get(id)


async def update(table: str, id: str, data: dict[str, Any]) -> Row | None:  # noqa: A002
    row = _table(table).get(id)
    if row is None:
        return None
    row = {**row, **data, "id": id}
    _table(table)[id] = row
    return row


async def remove(table: str, id: str) -> bool:  # noqa: A002
    return _table(table).pop(id, None) is not None
