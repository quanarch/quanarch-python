"""One logger per scope: the quanar's parts and each quan."""

from __future__ import annotations

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s")
# httpx writes every request the quanar makes; only its warnings are worth reading.
logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(scope: str) -> logging.Logger:
    return logging.getLogger(scope)
