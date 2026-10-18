from __future__ import annotations

from shop_qua import PermissionDefinition

from .constants import Permission

order_permissions = [
    PermissionDefinition(Permission.CREATE, "Place orders"),
    PermissionDefinition(Permission.READ, "See and cancel your own orders"),
    PermissionDefinition(Permission.READ_ALL, "See everyone's orders"),
]
