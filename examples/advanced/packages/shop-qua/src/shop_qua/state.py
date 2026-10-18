"""Where the quanar plugs its core in."""

from __future__ import annotations

from .types import QuanarCore

_core: QuanarCore | None = None


def init(core: QuanarCore) -> None:
    """Plugs the quanar's core in. Only the quanar calls this, once, before any quan runs."""
    global _core
    if _core is not None:
        raise RuntimeError("shop-qua is already initialized")
    _core = core


def reset() -> None:
    global _core
    _core = None


def is_initialized() -> bool:
    return _core is not None


def get_quanar_core() -> QuanarCore:
    if _core is None:
        raise RuntimeError("shop-qua is not initialized: the quanar must call init() first.")
    return _core
