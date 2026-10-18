"""One logger per scope: the quanar's parts and each quan."""

from __future__ import annotations

import json
import logging
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s")
# httpx writes every request the quanar makes; only its warnings are worth reading.
logging.getLogger("httpx").setLevel(logging.WARNING)


class ScopeLogger:
    """info, warn and error with optional data, the way a quan's log reaches the quanar."""

    def __init__(self, scope: str) -> None:
        self._log = logging.getLogger(scope)

    @staticmethod
    def _line(message: str, data: Any) -> str:
        return message if data is None else f"{message} {json.dumps(data, default=str)}"

    def info(self, message: str, data: Any = None) -> None:
        self._log.info(self._line(message, data))

    def warn(self, message: str, data: Any = None) -> None:
        self._log.warning(self._line(message, data))

    def error(self, message: str, data: Any = None) -> None:
        self._log.error(self._line(message, data))


def get_logger(scope: str) -> ScopeLogger:
    return ScopeLogger(scope)
