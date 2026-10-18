"""The products quan: the catalogue and its stock. It serves nothing itself; the quanar runs
what it declares here."""

from shop_qua import QuanManifest

from .apis import product_apis
from .constants import QUAN_NAME
from .events import order_events
from .models import product_model, reservation_model
from .permissions import product_permissions

manifest = QuanManifest(
    name=QUAN_NAME,
    version="1.0.0",
    models=[product_model, reservation_model],
    permissions=product_permissions,
    apis=product_apis,
    events=order_events,
)
