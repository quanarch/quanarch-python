from __future__ import annotations

from .constants import Permission, Role

#: Created on first start when there is no user at all, so the shop can be managed.
DEFAULT_ADMIN = {"email": "admin@shop.test", "name": "Admin", "password": "admin1234"}

#: What each role may do, across the shop. Other quans declare their permissions; deciding
#: who holds them is this quan's business, so the list lives here.
ROLE_PERMISSIONS: dict[Role, list[str]] = {
    Role.ADMIN: [Permission.READ, Permission.MANAGE, "products:manage", "orders:create", "orders:read", "orders:read-all"],
    Role.CUSTOMER: ["orders:create", "orders:read"],
}
