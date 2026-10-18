"""What a quan declares. The quanar's managers turn each declaration into something real:
a table, a route, a check, a subscription. A quan writes none of those by hand."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import KW_ONLY, dataclass

from .constants import FieldType, HttpMethod, QuanarMiddleware, RuleType
from .types import EventHandler, Handler, LocalMiddleware


@dataclass(frozen=True)
class FieldDefinition:
    type: FieldType
    _: KW_ONLY
    required: bool = False
    unique: bool = False
    index: bool = False
    default: str | int | float | bool | None = None
    #: For an enum.
    values: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelDefinition:
    """A table the quan owns. The quanar creates and migrates it; id, created_at and
    updated_at are added to every model."""

    name: str
    fields: Mapping[str, FieldDefinition]
    _: KW_ONLY
    #: Indexes over several fields.
    indexes: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class PermissionDefinition:
    """A permission a quan declares. Who holds it is not the quan's or the quanar's business."""

    #: Starts with the quan's name: products:manage
    key: str
    description: str


@dataclass(frozen=True)
class Rule:
    """One value's rule. The quanar checks it before the request reaches the quan."""

    type: RuleType
    _: KW_ONLY
    required: bool = False
    #: Length for strings and lists, value for numbers.
    min: float | None = None
    max: float | None = None
    #: A regular expression a string must match.
    pattern: str | None = None
    #: For an enum.
    values: tuple[str, ...] = ()
    #: For an array: the rule of each item.
    items: Rule | None = None
    #: For an object: the rule of each field.
    fields: Mapping[str, Rule] | None = None


@dataclass(frozen=True, kw_only=True)
class ValidationRules:
    params: Mapping[str, Rule] | None = None
    query: Mapping[str, Rule] | None = None
    body: Mapping[str, Rule] | None = None


@dataclass(frozen=True)
class ApiDefinition:
    """An api the quan asks the quanar to listen to. The quanar opens the route, runs its
    middlewares, checks its permissions and validation, and only then calls the handler."""

    #: Starts with the quan's name: /products, /products/{id}
    endpoint: str
    method: HttpMethod
    handler: Handler
    _: KW_ONLY
    #: Names run in the quanar; functions run in the quan. The quanar's always run first.
    middlewares: Sequence[QuanarMiddleware | LocalMiddleware] = ()
    #: Every permission is required. Implies authentication.
    permissions: Sequence[str] = ()
    validation: ValidationRules | None = None
    description: str = ""


@dataclass(frozen=True)
class EventSubscription:
    """An event a quan listens to. Emitters and listeners never know each other's code."""

    #: <quan>.<name>, for example orders.placed
    event: str
    handler: EventHandler


@dataclass(frozen=True, kw_only=True)
class QuanManifest:
    """Everything a quan is, declared. The quanar's quan registry turns it into a running quan."""

    name: str
    version: str
    apis: Sequence[ApiDefinition]
    models: Sequence[ModelDefinition] = ()
    permissions: Sequence[PermissionDefinition] = ()
    events: Sequence[EventSubscription] = ()
    #: Runs once the quanar has created the models and opened the apis.
    on_mount: Callable[[], Awaitable[None]] | None = None
    on_unmount: Callable[[], Awaitable[None]] | None = None
