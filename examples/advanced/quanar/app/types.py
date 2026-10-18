"""What the quanar keeps of a quan: everything it declared but its code, which stays in
the quan's process. These are the qua's definitions as they arrive, in JSON."""

from __future__ import annotations

from typing import Any, TypedDict


class FieldSpec(TypedDict):
    type: str
    required: bool
    unique: bool
    index: bool
    default: Any
    values: list[str]


class ModelSpec(TypedDict):
    name: str
    fields: dict[str, FieldSpec]
    indexes: list[list[str]]


class PermissionSpec(TypedDict):
    key: str
    description: str


class RuleSpec(TypedDict):
    type: str
    required: bool
    min: float | None
    max: float | None
    pattern: str | None
    values: list[str]
    items: RuleSpec | None
    fields: dict[str, RuleSpec] | None


class ValidationSpec(TypedDict):
    params: dict[str, RuleSpec] | None
    query: dict[str, RuleSpec] | None
    body: dict[str, RuleSpec] | None


class ApiMeta(TypedDict):
    endpoint: str
    method: str
    #: The quanar's middlewares, by name.
    middlewares: list[str]
    permissions: list[str]
    validation: ValidationSpec | None
    description: str
    #: How many of the quan's own middlewares run before its handler.
    local_middlewares: int


class ManifestMeta(TypedDict):
    name: str
    version: str
    models: list[ModelSpec]
    permissions: list[PermissionSpec]
    apis: list[ApiMeta]
    #: The events it listens to, in the order of its subscriptions.
    events: list[str]
