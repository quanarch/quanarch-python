from __future__ import annotations

from shop_qua import ApiDefinition, HttpMethod, QuanarMiddleware

from . import handlers, middlewares
from .constants import Permission, Route
from .validations import list_orders_validation, place_order_validation

order_apis = [
    ApiDefinition(
        Route.LIST,
        HttpMethod.POST,
        handlers.place_order,
        permissions=[Permission.CREATE],
        middlewares=[QuanarMiddleware.RATE_LIMIT],
        validation=place_order_validation,
        description="Place an order; it is confirmed or rejected once products answer",
    ),
    ApiDefinition(
        Route.LIST,
        HttpMethod.GET,
        handlers.list_orders,
        permissions=[Permission.READ],
        validation=list_orders_validation,
        description="Your orders, or everyone's with orders:read-all",
    ),
    ApiDefinition(
        Route.ONE,
        HttpMethod.GET,
        handlers.get_order,
        permissions=[Permission.READ],
        middlewares=[middlewares.own_order],
        description="One order",
    ),
    ApiDefinition(
        Route.CANCEL,
        HttpMethod.POST,
        handlers.cancel_order,
        permissions=[Permission.READ],
        middlewares=[middlewares.catch_errors, middlewares.own_order],
        description="Cancel an order; products give the stock back",
    ),
]
