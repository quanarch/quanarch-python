"""Checks a request against the rules an api declared, as data. Text values from the path and
query become numbers and booleans where a rule asks for them, so the quan receives them typed."""

from __future__ import annotations

import re
from typing import Any

from shop_qua import ValidationIssue

from ..types import RuleSpec, ValidationSpec

_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _coerce(rule: RuleSpec, value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if rule["type"] in ("integer", "number") and value.strip():
        try:
            number = float(value)
        except ValueError:
            return value
        return int(number) if rule["type"] == "integer" and number.is_integer() else number
    if rule["type"] == "boolean":
        return {"true": True, "false": False}.get(value, value)
    return value


def _number(value: float) -> str:
    return f"{value:g}"


def _check(rule: RuleSpec, value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if value is None or value == "":
        if rule["required"]:
            issues.append({"path": path, "message": "is required"})
        return

    def fail(message: str) -> None:
        issues.append({"path": path, "message": message})

    low, high = rule["min"], rule["max"]
    match rule["type"]:
        case "string" | "email" | "enum":
            if not isinstance(value, str):
                return fail("must be text")
            if rule["type"] == "email" and not _EMAIL.match(value):
                return fail("must be an email address")
            if rule["type"] == "enum" and value not in rule["values"]:
                return fail(f"must be one of {', '.join(rule['values'])}")
            if low is not None and len(value) < low:
                fail(f"must be at least {_number(low)} characters")
            if high is not None and len(value) > high:
                fail(f"must be at most {_number(high)} characters")
            if rule["pattern"] and not re.search(rule["pattern"], value):
                fail("has the wrong format")
        case "integer" | "number":
            if isinstance(value, bool) or not isinstance(value, int | float):
                return fail("must be a number")
            if rule["type"] == "integer" and not float(value).is_integer():
                return fail("must be a whole number")
            if low is not None and value < low:
                fail(f"must be at least {_number(low)}")
            if high is not None and value > high:
                fail(f"must be at most {_number(high)}")
        case "boolean":
            if not isinstance(value, bool):
                fail("must be true or false")
        case "array":
            if not isinstance(value, list):
                return fail("must be a list")
            if low is not None and len(value) < low:
                fail(f"must have at least {_number(low)} item{'' if low == 1 else 's'}")
            if high is not None and len(value) > high:
                fail(f"must have at most {_number(high)} item{'' if high == 1 else 's'}")
            items = rule["items"]
            if items is not None:
                for i, item in enumerate(value):
                    _check(items, item, f"{path}[{i}]", issues)
        case "object":
            if not isinstance(value, dict):
                return fail("must be an object")
            if rule["fields"]:
                _check_fields(rule["fields"], value, path, issues)


def _check_fields(fields: dict[str, RuleSpec], source: dict[str, Any], prefix: str, issues: list[ValidationIssue]) -> None:
    for name, rule in fields.items():
        path = f"{prefix}.{name}" if prefix else name
        if name in source:
            source[name] = _coerce(rule, source[name])
        _check(rule, source.get(name), path, issues)


def validate(rules: ValidationSpec, params: dict[str, Any], query: dict[str, Any], body: Any) -> list[ValidationIssue]:
    """Checks and coerces in place; returns every issue found."""
    issues: list[ValidationIssue] = []
    if rules["params"]:
        _check_fields(rules["params"], params, "params", issues)
    if rules["query"]:
        _check_fields(rules["query"], query, "query", issues)
    if rules["body"]:
        if not isinstance(body, dict):
            issues.append({"path": "body", "message": "must be a JSON object"})
        else:
            _check_fields(rules["body"], body, "body", issues)
    return issues
