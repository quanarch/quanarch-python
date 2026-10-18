"""The permissions quans declare. The quanar knows what each one means, not who holds it:
that comes in the token a quan asked for."""

from __future__ import annotations

from shop_qua import AuthUser

from ..types import PermissionSpec

_declared: dict[str, list[PermissionSpec]] = {}


def register(owner: str, permissions: list[PermissionSpec]) -> None:
    for permission in permissions:
        if not permission["key"].startswith(f"{owner}:"):
            raise ValueError(f"{owner} may not declare {permission['key']}: permissions start with {owner}:")
    _declared[owner] = permissions


def remove(owner: str) -> None:
    _declared.pop(owner, None)


def missing(user: AuthUser, required: list[str]) -> list[str]:
    """The required permissions the user lacks."""
    return [p for p in required if p not in user["permissions"]]


def all_permissions() -> list[PermissionSpec]:
    return [p for permissions in _declared.values() for p in permissions]
