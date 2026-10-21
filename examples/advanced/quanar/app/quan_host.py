"""The quan's own process.

The quanar starts one per quan, with an empty environment and a memory ceiling. This file is
quanar code, run on its own with `python -I`: the quan arrives as a zip in memory, declares what
it is, may import only its own package, the quas plugged into it and the standard modules listed
below, and cannot open files, sockets or other processes.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import builtins
import dataclasses
import importlib.abc
import io
import itertools
import json
import resource
import sys
import zipfile
from collections.abc import Callable, Coroutine, Mapping, Sequence
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any, cast

import shop_qua
from shop_qua import (
    ApiRequest,
    ApiResponse,
    DbOperation,
    EventMeta,
    IssuedToken,
    LocalMiddleware,
    QuanarMiddleware,
    QuanManifest,
    TokenClaims,
)

# The protocol owns the real stdout; whatever a quan prints goes to stderr.
_out = sys.stdout
sys.stdout = sys.stderr


def send(message: dict[str, Any]) -> None:
    _out.write(json.dumps(message, default=str) + "\n")
    _out.flush()


def _error_text(error: BaseException) -> str:
    return f"{type(error).__name__}: {error}"


# ---- capability calls go back to the quanar ----

_ids = itertools.count(1)
_pending: dict[int, asyncio.Future[Any]] = {}
#: Set from the quanar's --call-timeout as the host starts.
_call_timeout = 10.0


async def call(capability: str, *args: Any) -> Any:
    id_ = next(_ids)
    future = asyncio.get_running_loop().create_future()
    _pending[id_] = future
    send({"type": "call", "id": id_, "capability": capability, "args": list(args)})
    try:
        return await asyncio.wait_for(future, _call_timeout)
    except TimeoutError:
        raise TimeoutError(f"the quanar did not answer {capability} in {_call_timeout:g}s") from None
    finally:
        _pending.pop(id_, None)


class _Db:
    async def run(self, operation: DbOperation) -> Any:
        return await call("shop-qua:db.run", operation)

    async def transaction(self, operations: list[DbOperation]) -> list[Any]:
        return cast(list[Any], await call("shop-qua:db.transaction", operations))


class _Auth:
    async def issue_token(self, claims: TokenClaims) -> IssuedToken:
        return cast(IssuedToken, await call("shop-qua:auth.issue_token", claims))

    async def hash_password(self, password: str) -> str:
        return cast(str, await call("shop-qua:auth.hash_password", password))

    async def verify_password(self, password: str, hashed: str) -> bool:
        return cast(bool, await call("shop-qua:auth.verify_password", password, hashed))


class _Events:
    async def emit(self, event: str, payload: Any) -> None:
        await call("shop-qua:events.emit", event, payload)


class _Log:
    """A quan's log lines go to the quanar, which writes them under the quan's name."""

    def info(self, message: str, data: Any = None) -> None:
        send({"type": "log", "level": "info", "message": message, "data": data})

    def warn(self, message: str, data: Any = None) -> None:
        send({"type": "log", "level": "warn", "message": message, "data": data})

    def error(self, message: str, data: Any = None) -> None:
        send({"type": "log", "level": "error", "message": message, "data": data})


class _Core:
    def __init__(self) -> None:
        self.db = _Db()
        self.auth = _Auth()
        self.events = _Events()
        self.log = _Log()


#: Every qua this host can plug: its module name and how it gets its core.
QUAS: dict[str, tuple[str, Callable[[], None]]] = {
    "shop-qua": ("shop_qua", lambda: shop_qua.init(_Core())),
}

#: Standard modules a quan may import. Everything else is refused.
ALLOWED = {
    "abc", "asyncio", "collections", "contextlib", "copy", "dataclasses", "datetime", "decimal",
    "enum", "functools", "itertools", "json", "math", "operator", "random", "re", "statistics",
    "string", "textwrap", "time", "typing", "uuid", "__future__",
}


# ---- the quan's code, from the zip in memory ----

_host_import = builtins.__import__

class _QuanFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Loads the quan's own package from its zip, and gives its modules an import that only
    reaches what the quan was given: its own package, its plugged quas and the modules in
    ALLOWED. It looks at the name asked for, not at whether the host already loaded it."""

    def __init__(self, files: dict[str, str], allowed_quas: set[str]) -> None:
        self.files = files
        self.allowed_quas = allowed_quas
        self.top = {name.split("/")[0] for name in files}
        self.builtins = {**builtins.__dict__, "__import__": self._import}

    def _permitted(self, root: str) -> bool:
        return root in self.top or root in self.allowed_quas or root in ALLOWED

    def _import(
        self,
        name: str,
        globals: Mapping[str, object] | None = None,
        locals: Mapping[str, object] | None = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> ModuleType:
        # Relative imports (level > 0) stay inside the quan's own package.
        if level == 0 and not self._permitted(name.split(".")[0]):
            raise ImportError(f'"{name}" is not available to this quan')
        return _host_import(name, globals, locals, fromlist, level)

    def _source_path(self, fullname: str) -> tuple[str, bool] | None:
        base = fullname.replace(".", "/")
        if f"{base}/__init__.py" in self.files:
            return f"{base}/__init__.py", True
        if f"{base}.py" in self.files:
            return f"{base}.py", False
        return None

    def find_spec(
        self, fullname: str, path: Sequence[str] | None = None, target: ModuleType | None = None
    ) -> ModuleSpec | None:
        if fullname.split(".")[0] not in self.top:
            return None  # not the quan's own code: the normal machinery, behind _import
        found = self._source_path(fullname)
        if found is None:
            return None
        return ModuleSpec(fullname, self, is_package=found[1])

    def create_module(self, spec: ModuleSpec) -> None:
        return None  # the default module object

    def exec_module(self, module: ModuleType) -> None:
        found = self._source_path(module.__name__)
        if found is None:
            raise ImportError(f'"{module.__name__}" is not part of the quan')
        path, is_package = found
        if is_package:
            module.__path__ = []
        module.__dict__["__builtins__"] = self.builtins
        exec(compile(self.files[path], f"quan:{path}", "exec"), module.__dict__)


_BLOCKED_EVENTS = ("open", "socket.", "subprocess.", "os.system", "os.exec", "os.spawn", "os.posix_spawn", "os.fork", "ctypes.")


def _close_walls() -> None:
    """After the host has everything it needs: no files, no network, no processes."""

    def hook(event: str, _args: tuple[object, ...]) -> None:
        if event.startswith(_BLOCKED_EVENTS):
            raise PermissionError(f"{event} is not available to quans")

    sys.addaudithook(hook)


# ---- the quan ----

_manifest: QuanManifest | None = None
_locals: list[list[LocalMiddleware]] = []


def _plain(value: Any) -> Any:
    """A declaration as JSON: dataclasses become objects, tuples lists."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        value = dataclasses.asdict(value)
    return json.loads(json.dumps(value, default=list))


def load(name: str, code_b64: str, quas: list[str]) -> dict[str, Any]:
    global _manifest
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(code_b64))) as archive:
        files = {n: archive.read(n).decode("utf-8") for n in archive.namelist() if n.endswith(".py")}
    allowed = set()
    for qua in quas:
        if qua in QUAS:
            module_name, plug = QUAS[qua]
            plug()
            allowed.add(module_name)
    sys.meta_path.insert(0, _QuanFinder(files, allowed))
    _close_walls()

    module = importlib.import_module(name.replace("-", "_"))
    manifest = getattr(module, "manifest", None)
    if not isinstance(manifest, QuanManifest):
        raise TypeError(f"{name} declares no manifest: its package needs manifest = QuanManifest(...)")
    _manifest = manifest

    # The code stays here; the quanar gets what each api declares.
    apis = []
    for api in manifest.apis:
        local = [m for m in api.middlewares if not isinstance(m, str)]
        _locals.append(local)
        apis.append(
            {
                "endpoint": api.endpoint,
                "method": str(api.method),
                "middlewares": [str(m) for m in api.middlewares if isinstance(m, QuanarMiddleware)],
                "permissions": list(api.permissions),
                "validation": _plain(api.validation) if api.validation else None,
                "description": api.description,
                "local_middlewares": len(local),
            }
        )
    return {
        "name": manifest.name,
        "version": manifest.version,
        "models": [_plain(m) for m in manifest.models],
        "permissions": [_plain(p) for p in manifest.permissions],
        "apis": apis,
        "events": [s.event for s in manifest.events],
    }


async def handle(index: int, req: ApiRequest) -> ApiResponse:
    """The quan's own middlewares, then its handler. A middleware may answer without calling next."""
    assert _manifest is not None
    chain = _locals[index]
    handler = _manifest.apis[index].handler

    async def run(i: int) -> ApiResponse:
        if i < len(chain):
            return await chain[i](req, lambda: run(i + 1))
        return await handler(req)

    return await run(0)


async def _request(message: dict[str, Any]) -> None:
    try:
        send({"type": "response", "id": message["id"], "res": await handle(message["api"], message["req"])})
    except Exception as error:
        send({"type": "response", "id": message["id"], "error": _error_text(error)})


async def _event(message: dict[str, Any]) -> None:
    assert _manifest is not None
    try:
        meta = cast(EventMeta, message["meta"])
        await _manifest.events[message["subscription"]].handler(message["payload"], meta)
        send({"type": "delivered", "id": message["id"]})
    except Exception as error:
        send({"type": "delivered", "id": message["id"], "error": _error_text(error)})


async def _start() -> None:
    assert _manifest is not None
    try:
        if _manifest.on_mount is not None:
            await _manifest.on_mount()
        send({"type": "started"})
    except Exception as error:
        send({"type": "started", "error": _error_text(error)})


async def _unmount(done: asyncio.Event) -> None:
    try:
        if _manifest is not None and _manifest.on_unmount is not None:
            await _manifest.on_unmount()
    finally:
        done.set()


async def _read(done: asyncio.Event) -> None:
    """Never waits on the quan: start, requests, events and unmount each run on their own, so
    the answers to the quan's own calls keep arriving while they wait for them."""
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader(limit=16 * 1024 * 1024)
    await loop.connect_read_pipe(lambda: asyncio.StreamReaderProtocol(reader), sys.stdin)
    running: set[asyncio.Task[None]] = set()

    def spawn(work: Coroutine[Any, Any, None]) -> None:
        task = asyncio.create_task(work)
        running.add(task)
        task.add_done_callback(running.discard)

    while line := await reader.readline():
        message = json.loads(line)
        match message["type"]:
            case "load":
                try:
                    send({"type": "loaded", "manifest": load(message["name"], message["code"], message["quas"])})
                except Exception as error:
                    send({"type": "load-failed", "error": _error_text(error)})
            case "start":
                spawn(_start())
            case "request":
                spawn(_request(message))
            case "event":
                spawn(_event(message))
            case "result":
                future = _pending.pop(message["id"], None)
                if future and not future.done():
                    if "error" in message:
                        future.set_exception(RuntimeError(message["error"]))
                    else:
                        future.set_result(message.get("value"))
            case "unmount":
                spawn(_unmount(done))
    done.set()  # the quanar is gone


async def main() -> None:
    done = asyncio.Event()
    reading = asyncio.create_task(_read(done))
    await done.wait()
    reading.cancel()


def configure(argv: list[str]) -> None:
    """What the quanar asked for, set by the host itself before any quan code arrives:
    a memory ceiling, and how long a call to the quanar may take."""
    global _call_timeout
    parser = argparse.ArgumentParser(prog="quan_host")
    parser.add_argument("--memory-mb", type=int, required=True)
    parser.add_argument("--call-timeout", type=float, required=True)
    options = parser.parse_args(argv)
    size = options.memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (size, size))
    _call_timeout = options.call_timeout


if __name__ == "__main__":
    configure(sys.argv[1:])
    asyncio.run(main())
