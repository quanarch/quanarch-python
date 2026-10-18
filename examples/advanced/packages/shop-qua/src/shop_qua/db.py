"""The quan's view of the quanar's database. Every call becomes one DbOperation; the
quanar runs it against the quan's own tables.

    products: Repository[Product] = Repository("products")
    await products.find(where={"active": True}, order_by={"name": "asc"})
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, TypeVar, cast

from .state import get_quanar_core
from .types import DbOperation, Order, Where

T = TypeVar("T")


class Repository(Generic[T]):
    """One model of the quan, typed as the quan describes its rows."""

    def __init__(self, model: str) -> None:
        self.model = model

    async def _run(self, operation: DbOperation) -> Any:
        return await get_quanar_core().db.run(operation)

    async def find(
        self,
        *,
        where: Where | None = None,
        order_by: Mapping[str, Order] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[T]:
        operation: DbOperation = {"action": "find", "model": self.model}
        if where is not None:
            operation["where"] = where
        if order_by is not None:
            operation["order_by"] = order_by
        if limit is not None:
            operation["limit"] = limit
        if offset is not None:
            operation["offset"] = offset
        return cast(list[T], await self._run(operation))

    async def find_one(self, where: Where) -> T | None:
        return cast(T | None, await self._run({"action": "find_one", "model": self.model, "where": where}))

    async def find_by_id(self, id: str) -> T | None:  # noqa: A002
        return await self.find_one({"id": id})

    async def count(self, where: Where | None = None) -> int:
        return cast(int, await self._run({"action": "count", "model": self.model, "where": where or {}}))

    async def create(self, data: Mapping[str, Any]) -> T:
        return cast(T, await self._run({"action": "create", "model": self.model, "data": data}))

    async def update(self, where: Where, data: Mapping[str, Any]) -> int:
        """Returns how many rows changed."""
        return cast(int, await self._run({"action": "update", "model": self.model, "where": where, "data": data}))

    async def update_by_id(self, id: str, data: Mapping[str, Any]) -> T | None:  # noqa: A002
        await self.update({"id": id}, data)
        return await self.find_by_id(id)

    async def delete(self, where: Where) -> int:
        return cast(int, await self._run({"action": "delete", "model": self.model, "where": where}))


async def transaction(operations: list[DbOperation]) -> list[Any]:
    """Runs every operation or none."""
    return await get_quanar_core().db.transaction(operations)
