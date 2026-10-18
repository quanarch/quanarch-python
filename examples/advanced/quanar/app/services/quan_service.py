"""Follows each quan's event stream: load on open, reload on change, unmount on close."""

from __future__ import annotations

import asyncio
from typing import Any

from ..config import QuanSource, read_quan_sources, settings
from ..core import event_stream, get_logger, quan_loader, quan_registry
from ..utils import error_message

log = get_logger("quans")

_sources = read_quan_sources()
_states: dict[str, tuple[str, str | None]] = {}
_locks: dict[str, asyncio.Lock] = {}
_tasks: list[asyncio.Task[None]] = []


def _set_state(name: str, state: str, detail: str | None = None) -> None:
    if _states.get(name, ("",))[0] != state and state != "mounted":
        log.warn(f"{name}: {state}", detail)
    _states[name] = (state, detail)


async def _sync_one(source: QuanSource) -> None:
    try:
        code = await quan_loader.fetch(source)
        code_hash = quan_loader.verify(source, code)
    except (quan_loader.UnreachableError, quan_loader.HashMismatchError) as error:
        state = "unreachable" if isinstance(error, quan_loader.UnreachableError) else "hash-mismatch"
        _set_state(source.name, state, str(error))
        await quan_registry.unmount(source.name, state)
        return
    if quan_registry.code_hash(source.name) == code_hash:
        return
    try:
        await quan_registry.mount(source, code, code_hash, lambda exit: _set_state(source.name, "crashed", f"process exited with {exit}"))
        _set_state(source.name, "mounted")
    except Exception as error:
        _set_state(source.name, "failed", error_message(error))
        await quan_registry.unmount(source.name, "failed")


async def _sync(source: QuanSource) -> None:
    """One sync at a time per quan."""
    async with _locks.setdefault(source.name, asyncio.Lock()):
        await _sync_one(source)


async def _watch(source: QuanSource) -> None:
    _states[source.name] = ("pending", None)
    if source.events is None:
        await _sync(source)
        return

    async def on_event(name: str) -> None:
        if name == "change":
            await _sync(source)

    while True:
        await event_stream.follow(source.events, lambda: _sync(source), on_event)
        _set_state(source.name, "unreachable", f"{source.events} closed")
        await quan_registry.unmount(source.name, "its event stream closed")
        await asyncio.sleep(settings.reconnect_seconds)


def start() -> None:
    if not _sources:
        log.warn(f"no quans listed in {settings.quans_file}")
    for source in _sources:
        _tasks.append(asyncio.create_task(_watch(source)))


async def stop() -> None:
    for task in _tasks:
        task.cancel()
    for name in quan_registry.names():
        await quan_registry.unmount(name, "quanar stopping")


def status() -> list[dict[str, Any]]:
    return [
        {
            "name": s.name,
            "version": s.version,
            "quas": list(s.quas),
            "state": _states.get(s.name, ("pending", None))[0],
            "detail": _states.get(s.name, ("", None))[1],
            "pid": quan_registry.pid(s.name),
        }
        for s in _sources
    ]
