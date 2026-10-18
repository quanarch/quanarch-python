"""shop-qua: the contract between the shop's quanar and its quans.

A quan declares what it is with the definitions, and asks the quanar for work through
auth, db, events and log. Nothing here does that work: the quanar plugs its core in
with init().
"""

from . import auth, db, events, log
from .constants import FieldType, HttpMethod, QuanarMiddleware, RuleType
from .db import Repository
from .definitions import (
    ApiDefinition,
    EventSubscription,
    FieldDefinition,
    ModelDefinition,
    PermissionDefinition,
    QuanManifest,
    Rule,
    ValidationRules,
)
from .state import get_quanar_core, init, is_initialized, reset
from .types import (
    ApiRequest,
    ApiResponse,
    AuthCapability,
    AuthUser,
    DbCapability,
    DbOperation,
    EventHandler,
    EventMeta,
    EventsCapability,
    Handler,
    IssuedToken,
    LocalMiddleware,
    Logger,
    Next,
    Order,
    QuanarCore,
    Row,
    TokenClaims,
    ValidationIssue,
    Where,
)

__all__ = [
    "auth",
    "db",
    "events",
    "log",
    "init",
    "reset",
    "is_initialized",
    "get_quanar_core",
    "FieldType",
    "HttpMethod",
    "QuanarMiddleware",
    "RuleType",
    "Repository",
    "ApiDefinition",
    "EventSubscription",
    "FieldDefinition",
    "ModelDefinition",
    "PermissionDefinition",
    "QuanManifest",
    "Rule",
    "ValidationRules",
    "ApiRequest",
    "ApiResponse",
    "AuthCapability",
    "AuthUser",
    "DbCapability",
    "DbOperation",
    "EventHandler",
    "EventMeta",
    "EventsCapability",
    "Handler",
    "IssuedToken",
    "LocalMiddleware",
    "Logger",
    "Next",
    "Order",
    "QuanarCore",
    "Row",
    "TokenClaims",
    "ValidationIssue",
    "Where",
]
