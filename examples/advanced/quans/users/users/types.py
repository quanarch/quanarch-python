from __future__ import annotations

from typing import TypedDict

from .constants import Role


class User(TypedDict):
    id: str
    email: str
    name: str
    password_hash: str
    role: Role
    created_at: str
    updated_at: str


class PublicUser(TypedDict):
    """A user as anyone outside this quan sees it: never the password hash."""

    id: str
    email: str
    name: str
    role: Role
    created_at: str


class RegisterInput(TypedDict):
    email: str
    name: str
    password: str
