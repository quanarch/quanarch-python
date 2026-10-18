"""The words a quan and the quanar share. Each is a str, so it crosses as plain JSON."""

from __future__ import annotations

from enum import StrEnum


class FieldType(StrEnum):
    """Column types of a model. The quanar turns them into its database's types."""

    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    JSON = "json"
    ENUM = "enum"


class HttpMethod(StrEnum):
    """HTTP methods a quan can ask the quanar to listen to."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class QuanarMiddleware(StrEnum):
    """Middlewares the quanar provides. A quan names them in an api's middlewares;
    they run in the quanar, before the request reaches the quan."""

    #: Answers 401 unless the request carries a valid token.
    AUTHENTICATE = "authenticate"
    #: Answers 429 when one client calls the api too often.
    RATE_LIMIT = "rate-limit"


class RuleType(StrEnum):
    """Value types a validation rule checks."""

    STRING = "string"
    EMAIL = "email"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ENUM = "enum"
    ARRAY = "array"
    OBJECT = "object"
