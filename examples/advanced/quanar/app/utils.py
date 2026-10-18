"""Small helpers of the quanar."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Any

from .constants import ErrorCode


class HttpError(Exception):
    """An error that already knows how it should be answered."""

    def __init__(self, status: HTTPStatus, code: ErrorCode, message: str, details: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def error_message(error: BaseException) -> str:
    return str(error) or type(error).__name__
