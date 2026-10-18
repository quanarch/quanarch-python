"""Follows each quan's event stream: load on open, reload on change, unmount on close."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from ..config import QuanSource, settings
from ..core import QuanProcess, api_manager, event_stream, get_logger, quan_loader

log = get_logger("quans")


@dataclass
class Mounted:
    source: QuanSource
    code_hash: str
    process: QuanProcess


_mounted: dict[str, Mounted] = {}
_states: dict[str, tuple[str, str | None]] = {}
_locks: dict[str, asyncio.Lock] = {}
_tasks: list[asyncio.Task[None]] = []


def _set_state(name: str, state: str, detail: str | None = None) -> None:
    if _states.get(name, (None,))[0] != state and state != "mounted":
        log.warning("%s: %s %s", name, state, detail or "")
    _states[name] = (state, detail)


async def _unmount(name: str, reason: str) -> None:
    quan = _mounted.pop(name, None)
    if quan is None:
        return
    api_manager.forget(name)
    await quan.process.stop()
    log.warning("%s unmounted: %s", name, reason)


def _check_paths(name: str, listens: list[dict[str, str]]) -> None:
    for listen in listens:
        path = api_manager.normalize(listen["path"])
        if path != f"/{name}" and not path.startswith(f"/{name}/"):
            raise RuntimeError(f"{name} may not listen to {path}: paths start with /{name}")


def _forwarder(process: QuanProcess, index: int) -> api_manager.Forward:
    """Hands a request to the handler the quan registered at index."""

    async def forward(req: dict[str, Any]) -> dict[str, Any]:
        return await process.request(index, req)

    return forward


async def _mount(source: QuanSource, code: bytes, code_hash: str) -> None:
    process = QuanProcess(source)
    listens = await process.start(code)
    try:
        _check_paths(source.name, listens)
    except Exception:
        process.kill()
        raise
    await _unmount(source.name, "a new build arrived")
    for index, listen in enumerate(listens):
        api_manager.listen(source.name, listen["method"], listen["path"], _forwarder(process, index))
    _mounted[source.name] = Mounted(source, code_hash, process)
    _set_state(source.name, "mounted")

    def on_exit(code: int | None) -> None:
        if _mounted.get(source.name) and _mounted[source.name].process is process:
            api_manager.forget(source.name)
            _mounted.pop(source.name, None)
            _set_state(source.name, "crashed", f"process exited with {code}")

    process.on_exit.append(on_exit)
    log.info("%s mounted in pid %s, listening to %s", source.name, process.pid, ", ".join(api_manager.listening(source.name)) or "nothing")


async def _sync(source: QuanSource) -> None:
    async with _locks.setdefault(source.name, asyncio.Lock()):
        try:
            code = await quan_loader.fetch(source)
            code_hash = quan_loader.verify(source, code)
        except quan_loader.UnreachableError as error:
            _set_state(source.name, "unreachable", str(error))
            await _unmount(source.name, "unreachable")
            return
        except quan_loader.HashMismatchError as error:
            _set_state(source.name, "hash-mismatch", str(error))
            await _unmount(source.name, "hash-mismatch")
            return
        if _mounted.get(source.name) and _mounted[source.name].code_hash == code_hash:
            return
        try:
            await _mount(source, code, code_hash)
        except Exception as error:
            _set_state(source.name, "failed", str(error))
            await _unmount(source.name, "failed")


async def _watch(source: QuanSource) -> None:
    _states[source.name] = ("pending", None)
    if source.events is None:
        await _sync(source)
        return
    while True:
        async def on_event(name: str) -> None:
            if name == "change":
                await _sync(source)

        await event_stream.follow(source.events, lambda: _sync(source), on_event)
        _set_state(source.name, "unreachable", f"{source.events} closed")
        await _unmount(source.name, "its event stream closed")
        await asyncio.sleep(settings.reconnect_seconds)


def start() -> None:
    for source in settings.quan_sources:
        _tasks.append(asyncio.create_task(_watch(source)))


async def stop() -> None:
    for task in _tasks:
        task.cancel()
    for name in [*_mounted]:
        await _unmount(name, "quanar stopping")


def status() -> list[dict[str, Any]]:
    return [
        {
            "name": s.name,
            "quas": list(s.quas),
            "state": _states.get(s.name, ("pending", None))[0],
            "detail": _states.get(s.name, (None, None))[1],
            "pid": _mounted[s.name].process.pid if s.name in _mounted else None,
            "listening": api_manager.listening(s.name),
        }
        for s in settings.quan_sources
    ]
