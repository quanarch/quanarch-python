"""Codes and paths of the quanar itself. Everything else belongs to quans."""

from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    """Codes the quanar answers with; the client can rely on them."""

    NOT_FOUND = "not_found"
    UNAUTHENTICATED = "unauthenticated"
    FORBIDDEN = "forbidden"
    VALIDATION = "validation_failed"
    RATE_LIMITED = "rate_limited"
    BAD_REQUEST = "bad_request"
    TOO_LARGE = "too_large"
    QUAN_UNAVAILABLE = "quan_unavailable"
    QUAN_TIMEOUT = "quan_timeout"
    QUAN_FAILED = "quan_failed"
    INTERNAL = "internal"


class SystemRoute(StrEnum):
    HEALTH = "/health"
    QUANS = "/quans"
