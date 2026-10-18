"""The quanar's side of each qua, bound to one quan: its database calls reach only its tables,
its events carry its name. A quan's process asks for a capability by name; only the quas
plugged into that quan can be reached."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from shop_qua import DbOperation, IssuedToken, TokenClaims

from . import auth_manager, db_manager, event_manager

Capability = Callable[..., Awaitable[Any]]


def _shop_qua(owner: str) -> dict[str, Capability]:
    async def run(op: DbOperation) -> Any:
        return await db_manager.run(owner, op)

    async def transaction(ops: list[DbOperation]) -> list[Any]:
        return await db_manager.transaction(owner, ops)

    async def issue_token(claims: TokenClaims) -> IssuedToken:
        return auth_manager.issue_token(claims)

    async def emit(event: str, payload: Any) -> None:
        event_manager.publish(owner, event, payload)

    return {
        "db.run": run,
        "db.transaction": transaction,
        "auth.issue_token": issue_token,
        "auth.hash_password": auth_manager.hash_password,
        "auth.verify_password": auth_manager.verify_password,
        "events.emit": emit,
    }


QUA_CORES: dict[str, Callable[[str], dict[str, Capability]]] = {
    "shop-qua": _shop_qua,
}


def plugged(owner: str, quas: tuple[str, ...]) -> dict[str, Capability]:
    return {f"{qua}:{name}": fn for qua in quas if qua in QUA_CORES for name, fn in QUA_CORES[qua](owner).items()}
