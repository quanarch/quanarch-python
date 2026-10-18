"""Turns the models a quan declares into tables, and keeps them in step."""

from __future__ import annotations

import re

from ..types import FieldSpec, ModelSpec
from .database import database
from .logger import get_logger

log = get_logger("schema")

_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
RESERVED = ("id", "created_at", "updated_at")
_COLUMN = {
    "string": "TEXT",
    "text": "TEXT",
    "enum": "TEXT",
    "datetime": "TEXT",
    "json": "TEXT",
    "integer": "INTEGER",
    "boolean": "INTEGER",
    "number": "REAL",
}
_RESERVED_FIELD: FieldSpec = {"type": "string", "required": False, "unique": False, "index": False, "default": None, "values": []}

# owner → model name → definition
_registry: dict[str, dict[str, ModelSpec]] = {}


def quote(name: str) -> str:
    return f'"{name}"'


def table_name(owner: str, model: str) -> str:
    """Every quan's tables live in the same database, each under its own prefix."""
    return f"{owner.replace('-', '_')}__{model}"


def _check(owner: str, model: ModelSpec) -> None:
    if not _NAME.match(model["name"]):
        raise ValueError(f'{owner}: model name "{model["name"]}" must be lowercase letters, digits and _')
    for name, spec in model["fields"].items():
        where = f"{owner}.{model['name']}.{name}"
        if name in RESERVED:
            raise ValueError(f"{where} is added by the quanar")
        if not _NAME.match(name):
            raise ValueError(f"{where}: field names are lowercase letters, digits and _")
        if spec["type"] not in _COLUMN:
            raise ValueError(f"{where}: unknown type {spec['type']}")
        if spec["type"] == "enum" and not spec["values"]:
            raise ValueError(f"{where}: an enum needs values")
    for index in model["indexes"]:
        for name in index:
            if name not in model["fields"] and name not in RESERVED:
                raise ValueError(f"{owner}.{model['name']}: index over unknown field {name}")


def sync(owner: str, models: list[ModelSpec]) -> None:
    """A new model becomes a table, a new field a column, a unique or indexed field an index.
    Nothing is ever dropped, so a quan going away or coming back never loses data."""
    for model in models:
        _check(owner, model)
    changes: list[str] = []

    for model in models:
        table = table_name(owner, model["name"])
        existing = {row["name"] for row in database.execute(f"PRAGMA table_info({quote(table)})")}
        if not existing:
            columns = "".join(f"{quote(f)} {_COLUMN[s['type']]}, " for f, s in model["fields"].items())
            database.execute(f'CREATE TABLE {quote(table)} ("id" TEXT PRIMARY KEY, {columns}"created_at" TEXT NOT NULL, "updated_at" TEXT NOT NULL)')
            changes.append(f"created {table}")
        else:
            for name, spec in model["fields"].items():
                if name not in existing:
                    database.execute(f"ALTER TABLE {quote(table)} ADD COLUMN {quote(name)} {_COLUMN[spec['type']]}")
                    changes.append(f"added {table}.{name}")

        indexes = [([f], s["unique"]) for f, s in model["fields"].items() if s["unique"] or s["index"]]
        indexes += [(list(fields), False) for fields in model["indexes"]]
        for fields, unique in indexes:
            name = f"{table}__{'_'.join(fields)}{'__unique' if unique else ''}"
            columns = ", ".join(quote(f) for f in fields)
            database.execute(f"CREATE {'UNIQUE ' if unique else ''}INDEX IF NOT EXISTS {quote(name)} ON {quote(table)} ({columns})")

    _registry[owner] = {m["name"]: m for m in models}
    if changes:
        log.info(f"{owner}: {', '.join(changes)}")


def remove(owner: str) -> None:
    _registry.pop(owner, None)


def model(owner: str, name: str) -> ModelSpec:
    """A model of the quan, or an error: a quan can only reach its own tables."""
    found = _registry.get(owner, {}).get(name)
    if found is None:
        raise LookupError(f"{owner} has no model {name}")
    return found


def field(spec: ModelSpec, name: str) -> FieldSpec | None:
    if name in RESERVED:
        return _RESERVED_FIELD
    return spec["fields"].get(name)


def describe() -> dict[str, list[ModelSpec]]:
    return {owner: [*models.values()] for owner, models in _registry.items()}
