"""Runs the operations quans send, against their own tables only. Every value goes in as a
parameter, every name is checked against the model, booleans and json come back as stored."""

from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Mapping
from typing import Any

from shop_qua import DbOperation, Row, Where

from ..types import FieldSpec, ModelSpec
from ..utils import now_iso
from . import schema_manager
from .database import database
from .schema_manager import quote, table_name

MAX_LIMIT = 500
_OPERATORS = {"eq": "=", "ne": "!=", "gt": ">", "gte": ">=", "lt": "<", "lte": "<=", "like": "LIKE"}


class DbError(Exception):
    """A problem with an operation itself: the quan sent something its model does not allow."""


def _field(model: ModelSpec, name: str) -> FieldSpec:
    found = schema_manager.field(model, name)
    if found is None:
        raise DbError(f"{model['name']} has no field {name}")
    return found


def _encode(model: ModelSpec, name: str, value: Any) -> Any:
    if value is None:
        return None
    spec = _field(model, name)
    where = f"{model['name']}.{name}"
    match spec["type"]:
        case "boolean":
            if not isinstance(value, bool):
                raise DbError(f"{where} must be true or false")
            return int(value)
        case "integer" | "number":
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise DbError(f"{where} must be a number")
            if spec["type"] == "integer" and not float(value).is_integer():
                raise DbError(f"{where} must be a whole number")
            return value
        case "json":
            return json.dumps(value)
        case "enum":
            if str(value) not in spec["values"]:
                raise DbError(f"{where} must be one of {', '.join(spec['values'])}")
            return str(value)
        case _:
            if not isinstance(value, str):
                raise DbError(f"{where} must be text")
            return value


def _decode(model: ModelSpec, row: sqlite3.Row) -> Row:
    out: Row = {}
    for name in row.keys():
        value = row[name]
        spec = schema_manager.field(model, name)
        if value is None or spec is None:
            out[name] = value
        elif spec["type"] == "boolean":
            out[name] = value == 1
        elif spec["type"] == "json":
            out[name] = json.loads(value)
        else:
            out[name] = value
    return out


def _where(model: ModelSpec, where: Where | None, params: list[Any]) -> str:
    parts: list[str] = []
    for name, condition in (where or {}).items():
        _field(model, name)
        column = quote(name)
        if condition is None:
            parts.append(f"{column} IS NULL")
        elif isinstance(condition, Mapping):
            for op, value in condition.items():
                if op == "in":
                    if not isinstance(value, list) or not value:
                        parts.append("0")
                        continue
                    parts.append(f"{column} IN ({', '.join('?' for _ in value)})")
                    params.extend(_encode(model, name, v) for v in value)
                elif op in _OPERATORS:
                    parts.append(f"{column} {_OPERATORS[op]} ?")
                    params.append(str(value) if op == "like" else _encode(model, name, value))
                else:
                    raise DbError(f"unknown operator {op}")
        else:
            parts.append(f"{column} = ?")
            params.append(_encode(model, name, condition))
    return f" WHERE {' AND '.join(parts)}" if parts else ""


def _find_sql(model: ModelSpec, table: str, op: DbOperation, params: list[Any]) -> str:
    sql = f"SELECT * FROM {quote(table)}{_where(model, op.get('where'), params)}"
    order = op.get("order_by") or {}
    if order:
        terms = []
        for name, direction in order.items():
            _field(model, name)
            terms.append(f"{quote(name)} {'DESC' if direction == 'desc' else 'ASC'}")
        sql += f" ORDER BY {', '.join(terms)}"
    params += [min(op.get("limit", MAX_LIMIT), MAX_LIMIT), op.get("offset", 0)]
    return sql + " LIMIT ? OFFSET ?"


def _changes(model: ModelSpec, name: str, value: Any, params: list[Any]) -> str:
    if name in schema_manager.RESERVED:
        raise DbError(f"{name} cannot be changed")
    if isinstance(value, Mapping) and ("increment" in value or "decrement" in value):
        if _field(model, name)["type"] not in ("integer", "number"):
            raise DbError(f"{model['name']}.{name} is not a number")
        params.append(value["increment"] if "increment" in value else -value["decrement"])
        return f"{quote(name)} = {quote(name)} + ?"
    params.append(_encode(model, name, value))
    return f"{quote(name)} = ?"


def _execute(owner: str, op: DbOperation) -> Any:
    model = schema_manager.model(owner, op["model"])
    table = table_name(owner, op["model"])
    params: list[Any] = []

    match op["action"]:
        case "find":
            return [_decode(model, r) for r in database.execute(_find_sql(model, table, op, params), params)]

        case "find_one":
            row = database.execute(_find_sql(model, table, {**op, "limit": 1}, params), params).fetchone()
            return _decode(model, row) if row else None

        case "count":
            sql = f"SELECT COUNT(*) FROM {quote(table)}{_where(model, op.get('where'), params)}"
            return database.execute(sql, params).fetchone()[0]

        case "create":
            data = dict(op.get("data", {}))
            for name, spec in model["fields"].items():
                if data.get(name) is None and spec["default"] is not None:
                    data[name] = spec["default"]
                if spec["required"] and data.get(name) is None:
                    raise DbError(f"{model['name']}.{name} is required")
            now = now_iso()
            row = {"id": str(uuid.uuid4()), **data, "created_at": now, "updated_at": now}
            names = list(row)
            database.execute(
                f"INSERT INTO {quote(table)} ({', '.join(quote(n) for n in names)}) VALUES ({', '.join('?' for _ in names)})",
                [_encode(model, n, row[n]) for n in names],
            )
            return _decode(model, database.execute(f'SELECT * FROM {quote(table)} WHERE "id" = ?', [row["id"]]).fetchone())

        case "update":
            sets = [_changes(model, name, value, params) for name, value in op.get("data", {}).items()]
            sets.append('"updated_at" = ?')
            params.append(now_iso())
            changed = database.execute(f"UPDATE {quote(table)} SET {', '.join(sets)}{_where(model, op.get('where'), params)}", params).rowcount
            if "expect" in op and changed != op["expect"]:
                raise DbError(f"expected {op['expect']} {model['name']} to change, {changed} did")
            return changed

        case "delete":
            changed = database.execute(f"DELETE FROM {quote(table)}{_where(model, op.get('where'), params)}", params).rowcount
            if "expect" in op and changed != op["expect"]:
                raise DbError(f"expected {op['expect']} {model['name']} to be deleted, {changed} were")
            return changed


def _explain(owner: str, error: Exception) -> DbError:
    """Turns SQLite's messages into ones a quan can act on."""
    if isinstance(error, DbError):
        return error
    message = str(error)
    if message.startswith("UNIQUE constraint failed: "):
        return DbError(f"{message.rsplit('.', 1)[-1]} must be unique")
    return DbError(f"{owner}: {message}")


async def run(owner: str, op: DbOperation) -> Any:
    try:
        return _execute(owner, op)
    except (DbError, LookupError, sqlite3.Error) as error:
        raise _explain(owner, error) from None


async def transaction(owner: str, ops: list[DbOperation]) -> list[Any]:
    """Every operation or none."""
    database.execute("BEGIN IMMEDIATE")
    try:
        results = [_execute(owner, op) for op in ops]
    except (DbError, LookupError, sqlite3.Error) as error:
        database.execute("ROLLBACK")
        raise _explain(owner, error) from None
    database.execute("COMMIT")
    return results
