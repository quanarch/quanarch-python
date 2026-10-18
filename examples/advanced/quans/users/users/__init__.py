"""The users quan: accounts, roles and sign-in. It serves nothing itself; the quanar runs what
it declares here."""

from shop_qua import QuanManifest

from . import services
from .apis import user_apis
from .constants import QUAN_NAME
from .models import user_model
from .permissions import user_permissions

# This quan listens to no events; it only emits users.registered.
manifest = QuanManifest(
    name=QUAN_NAME,
    version="1.0.0",
    models=[user_model],
    permissions=user_permissions,
    apis=user_apis,
    on_mount=services.ensure_admin,
)
