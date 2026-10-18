from __future__ import annotations

from shop_qua import ApiDefinition, HttpMethod, QuanarMiddleware

from . import handlers, middlewares
from .constants import Permission, Route
from .validations import login_validation, register_validation, role_validation

user_apis = [
    ApiDefinition(
        Route.REGISTER,
        HttpMethod.POST,
        handlers.register,
        middlewares=[QuanarMiddleware.RATE_LIMIT, middlewares.catch_errors],
        validation=register_validation,
        description="Create an account",
    ),
    ApiDefinition(
        Route.LOGIN,
        HttpMethod.POST,
        handlers.login,
        middlewares=[QuanarMiddleware.RATE_LIMIT, middlewares.catch_errors],
        validation=login_validation,
        description="Sign in and get a token",
    ),
    ApiDefinition(
        Route.ME,
        HttpMethod.GET,
        handlers.me,
        middlewares=[QuanarMiddleware.AUTHENTICATE, middlewares.catch_errors],
        description="The signed-in user",
    ),
    ApiDefinition(
        Route.LIST,
        HttpMethod.GET,
        handlers.list_users,
        permissions=[Permission.READ],
        description="Every user",
    ),
    ApiDefinition(
        Route.ROLE,
        HttpMethod.PUT,
        handlers.set_role,
        permissions=[Permission.MANAGE],
        middlewares=[middlewares.catch_errors, middlewares.audit],
        validation=role_validation,
        description="Change a user's role",
    ),
]
