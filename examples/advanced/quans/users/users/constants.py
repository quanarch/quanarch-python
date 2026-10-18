from __future__ import annotations

from enum import StrEnum

QUAN_NAME = "users"


class Route(StrEnum):
    """Every endpoint starts with the quan's name."""

    REGISTER = "/users/register"
    LOGIN = "/users/login"
    ME = "/users/me"
    LIST = "/users"
    ROLE = "/users/{id}/role"


class Permission(StrEnum):
    READ = "users:read"
    MANAGE = "users:manage"


class Role(StrEnum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class Model(StrEnum):
    USERS = "users"


class Event(StrEnum):
    """Events this quan emits."""

    REGISTERED = "users.registered"
