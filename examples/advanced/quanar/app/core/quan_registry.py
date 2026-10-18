"""Turns what a quan declared into a running quan, through the managers: its models become
tables, its permissions become known, its apis are opened, its subscriptions start receiving
events, and only then does it start."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..config import QuanSource
from . import api_manager, event_manager, permission_manager, schema_manager
from .logger import get_logger
from .quan_process import QuanProcess

log = get_logger("registry")


@dataclass
class Mounted:
    source: QuanSource
    code_hash: str
    process: QuanProcess


_mounted: dict[str, Mounted] = {}


async def mount(source: QuanSource, code: bytes, code_hash: str, on_crash: Callable[[int | None], None]) -> None:
    process = QuanProcess(source)
    try:
        manifest = await process.load(code)
        if manifest["name"] != source.name:
            raise ValueError(f'the manifest says "{manifest["name"]}", the list says "{source.name}"')

        await unmount(source.name, f"{manifest['version']} arrived")

        schema_manager.sync(source.name, manifest["models"])
        permission_manager.register(source.name, manifest["permissions"])
        api_manager.create(source.name, manifest["apis"], process.request)
        event_manager.subscribe(source.name, manifest["events"], process.deliver)
        _mounted[source.name] = Mounted(source, code_hash, process)
        await process.start()
    except BaseException:
        process.kill()
        if source.name in _mounted and _mounted[source.name].process is process:
            release(source.name)
        raise

    def on_exit(code: int | None) -> None:
        if source.name in _mounted and _mounted[source.name].process is process:
            release(source.name)
            on_crash(code)

    process.on_exit.append(on_exit)
    log.info(
        f"{source.name}@{manifest['version']} mounted in pid {process.pid}: {len(manifest['apis'])} apis, "
        f"{len(manifest['models'])} models, {len(manifest['events'])} subscriptions"
    )


async def unmount(name: str, reason: str) -> None:
    quan = _mounted.get(name)
    if quan is None:
        return
    release(name)
    await quan.process.stop()
    log.warn(f"{name} unmounted: {reason}")


def release(name: str) -> None:
    """Takes a quan out of every manager. Its tables and rows stay."""
    api_manager.remove(name)
    event_manager.forget(name)
    permission_manager.remove(name)
    schema_manager.remove(name)
    _mounted.pop(name, None)


def code_hash(name: str) -> str | None:
    return _mounted[name].code_hash if name in _mounted else None


def pid(name: str) -> int | None:
    return _mounted[name].process.pid if name in _mounted else None


def names() -> list[str]:
    return [*_mounted]
