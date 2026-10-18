from __future__ import annotations

from shop_qua import ApiDefinition, HttpMethod

from . import handlers, middlewares
from .constants import Permission, Route
from .validations import create_product_validation, list_products_validation, restock_validation, update_product_validation

product_apis = [
    ApiDefinition(
        Route.LIST,
        HttpMethod.GET,
        handlers.list_products,
        validation=list_products_validation,
        description="The catalogue; managers also see inactive products",
    ),
    ApiDefinition(
        Route.ONE,
        HttpMethod.GET,
        handlers.get_product,
        middlewares=[middlewares.load_product],
        description="One product",
    ),
    ApiDefinition(
        Route.LIST,
        HttpMethod.POST,
        handlers.create_product,
        permissions=[Permission.MANAGE],
        middlewares=[middlewares.catch_errors],
        validation=create_product_validation,
        description="Add a product",
    ),
    ApiDefinition(
        Route.ONE,
        HttpMethod.PATCH,
        handlers.update_product,
        permissions=[Permission.MANAGE],
        middlewares=[middlewares.catch_errors, middlewares.load_product],
        validation=update_product_validation,
        description="Change a product",
    ),
    ApiDefinition(
        Route.RESTOCK,
        HttpMethod.POST,
        handlers.restock_product,
        permissions=[Permission.MANAGE],
        middlewares=[middlewares.catch_errors, middlewares.load_product],
        validation=restock_validation,
        description="Add stock",
    ),
]
