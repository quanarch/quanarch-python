"""The quan's log lines, written by the quanar under the quan's name."""

from __future__ import annotations

from typing import Any

from .state import get_quanar_core


def info(message: str, data: Any = None) -> None:
    get_quanar_core().log.info(message, data)


def warn(message: str, data: Any = None) -> None:
    get_quanar_core().log.warn(message, data)


def error(message: str, data: Any = None) -> None:
    get_quanar_core().log.error(message, data)
