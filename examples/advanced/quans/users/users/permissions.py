from __future__ import annotations

from shop_qua import PermissionDefinition

from .constants import Permission

user_permissions = [
    PermissionDefinition(Permission.READ, "See every user"),
    PermissionDefinition(Permission.MANAGE, "Change what a user may do"),
]
