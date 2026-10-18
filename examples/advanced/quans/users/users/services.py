from __future__ import annotations

from typing import Any

from shop_qua import Repository, auth, events, log

from .config import DEFAULT_ADMIN, ROLE_PERMISSIONS
from .constants import Event, Model, Role
from .errors import AppError
from .types import PublicUser, RegisterInput, User

_users: Repository[User] = Repository(Model.USERS)


def _public(user: User) -> PublicUser:
    return {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"], "created_at": user["created_at"]}


def _wrong_credentials() -> AppError:
    """The same answer for a wrong email and a wrong password: which one was wrong is not told."""
    return AppError(401, "wrong_credentials", "Email or password is wrong")


async def register(data: RegisterInput) -> PublicUser:
    email = data["email"].lower()
    if await _users.find_one({"email": email}):
        raise AppError(409, "email_taken", "This email is already registered")
    user = await _users.create(
        {
            "email": email,
            "name": data["name"].strip(),
            "password_hash": await auth.hash_password(data["password"]),
            "role": Role.CUSTOMER,
        }
    )
    await events.emit(Event.REGISTERED, {"user_id": user["id"], "email": user["email"]})
    return _public(user)


async def login(email: str, password: str) -> dict[str, Any]:
    user = await _users.find_one({"email": email.lower()})
    if user is None or not await auth.verify_password(password, user["password_hash"]):
        raise _wrong_credentials()
    permissions = ROLE_PERMISSIONS[Role(user["role"])]
    issued = await auth.issue_token({"sub": user["id"], "name": user["name"], "permissions": permissions})
    return {**issued, "user": _public(user), "permissions": permissions}


async def me(id: str) -> PublicUser:  # noqa: A002
    user = await _users.find_by_id(id)
    if user is None:
        raise AppError(404, "user_not_found", "This user no longer exists")
    return _public(user)


async def list_users() -> list[PublicUser]:
    return [_public(u) for u in await _users.find(order_by={"created_at": "asc"})]


async def set_role(id: str, role: Role, by: str) -> PublicUser:  # noqa: A002
    if id == by:
        raise AppError(409, "own_role", "You cannot change your own role")
    user = await _users.update_by_id(id, {"role": role})
    if user is None:
        raise AppError(404, "user_not_found", "No such user")
    return _public(user)


async def ensure_admin() -> None:
    """On the very first start there is nobody to manage the shop: an admin is created."""
    if await _users.count() > 0:
        return
    await _users.create(
        {
            "email": DEFAULT_ADMIN["email"],
            "name": DEFAULT_ADMIN["name"],
            "password_hash": await auth.hash_password(DEFAULT_ADMIN["password"]),
            "role": Role.ADMIN,
        }
    )
    log.warn(f"created {DEFAULT_ADMIN['email']} with the default password; change it")
