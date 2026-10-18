"""The orders quan. It never reads the products' tables: it announces an order and follows
what products answer. It serves nothing itself; the quanar runs what it declares here."""

from shop_qua import QuanManifest

from .apis import order_apis
from .constants import QUAN_NAME
from .events import product_events
from .models import order_model
from .permissions import order_permissions

manifest = QuanManifest(
    name=QUAN_NAME,
    version="1.0.0",
    models=[order_model],
    permissions=order_permissions,
    apis=order_apis,
    events=product_events,
)
