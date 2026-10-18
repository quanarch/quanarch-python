"""One quan in its own process: started with python -I, an empty environment and a memory
ceiling. The quanar talks to it only through JSON lines."""

from __future__ import annotations

import asyncio
import base64
import itertools
import json
import sys
from collections.abc import Callable
from http import HTTPStatus
from pathlib import Path
from typing import Any, cast

from shop_qua import ApiRequest, ApiResponse, EventMeta

from ..config import QuanSource, settings
from ..constants import ErrorCode
from ..types import ManifestMeta
from ..utils import HttpError
from .logger import get_logger
from .qua_core import plugged

HOST = Path(__file__).resolve().parent.parent / "quan_host.py"


class QuanStopped(Exception):
    pass


class QuanProcess:
    def __init__(self, source: QuanSource) -> None:
        self.source = source
        self.log = get_logger(source.name)
        self.capabilities = plugged(source.name, source.quas)
        self._ids = itertools.count(1)
        self._waiting: dict[int, asyncio.Future[Any]] = {}
        #: loaded and started: answers the quan gives once.
        self._once: dict[str, asyncio.Future[Any]] = {}
        self._proc: asyncio.subprocess.Process | None = None
        self._reader: asyncio.Task[None] | None = None
        self._calls: set[asyncio.Task[None]] = set()
        self.on_exit: list[Callable[[int | None], None]] = []

    @property
    def pid(self) -> int | None:
        return self._proc.pid if self._proc else None

    async def load(self, code: bytes) -> ManifestMeta:
        """Starts the quan's process, sends the code in, waits for everything it declared."""
        # The host sets its own memory ceiling and call timeout before any quan code arrives.
        self._proc = await asyncio.create_subprocess_exec(
            sys.executable, "-I", str(HOST),
            "--memory-mb", str(settings.quan_memory_mb),
            "--call-timeout", str(settings.call_timeout_seconds),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            env={},  # no secrets, no addresses, nothing of the quanar's
            limit=16 * 1024 * 1024,
        )
        self._reader = asyncio.create_task(self._read())
        message = {"type": "load", "name": self.source.name, "code": base64.b64encode(code).decode(), "quas": list(self.source.quas)}
        return cast(ManifestMeta, await self._once_answer("loaded", message))

    async def start(self) -> None:
        """Lets the quan run its on_mount, once its models and apis are in place."""
        await self._once_answer("started", {"type": "start"})

    async def request(self, api: int, req: ApiRequest) -> ApiResponse:
        try:
            return cast(ApiResponse, await self._ask({"type": "request", "api": api, "req": req}))
        except TimeoutError:
            # A quan stuck in a loop is shut down; its process goes, the quanar stays.
            self.log.error(f"no answer to {req['method']} {req['path']} in {settings.request_timeout_seconds:g}s, stopping it")
            self.kill()
            raise HttpError(HTTPStatus.GATEWAY_TIMEOUT, ErrorCode.QUAN_TIMEOUT, f"{self.source.name} did not answer") from None
        except QuanStopped:
            raise HttpError(HTTPStatus.SERVICE_UNAVAILABLE, ErrorCode.QUAN_UNAVAILABLE, f"{self.source.name} stopped") from None
        except RuntimeError as error:
            self.log.error(f"{req['method']} {req['path']} failed", str(error))
            raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, ErrorCode.QUAN_FAILED, f"{self.source.name} failed") from None

    async def deliver(self, subscription: int, payload: Any, meta: EventMeta) -> None:
        await self._ask({"type": "event", "subscription": subscription, "payload": payload, "meta": meta})

    async def stop(self) -> None:
        """Asks the quan to clean up, then makes sure its process is gone."""
        if not self._proc or self._proc.returncode is not None:
            return
        self._send({"type": "unmount"})
        try:
            await asyncio.wait_for(self._proc.wait(), 2)
        except TimeoutError:
            self.kill()

    def kill(self) -> None:
        if self._proc and self._proc.returncode is None:
            self._proc.kill()

    async def _once_answer(self, kind: str, message: dict[str, Any]) -> Any:
        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self._once[kind] = future
        self._send(message)
        try:
            return await asyncio.wait_for(future, settings.load_timeout_seconds)
        except BaseException:
            self.kill()
            raise

    async def _ask(self, message: dict[str, Any]) -> Any:
        id_ = next(self._ids)
        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self._waiting[id_] = future
        self._send({**message, "id": id_})
        try:
            return await asyncio.wait_for(future, settings.request_timeout_seconds)
        finally:
            self._waiting.pop(id_, None)

    def _send(self, message: dict[str, Any]) -> None:
        if self._proc and self._proc.stdin and not self._proc.stdin.is_closing():
            self._proc.stdin.write((json.dumps(message) + "\n").encode())

    def _settle(self, id_: int, error: str | None, value: Any) -> None:
        future = self._waiting.get(id_)
        if future is None or future.done():
            return
        if error is not None:
            future.set_exception(RuntimeError(error))
        else:
            future.set_result(value)

    def _settle_once(self, kind: str, error: str | None, value: Any) -> None:
        future = self._once.pop(kind, None)
        if future is None or future.done():
            return
        if error is not None:
            future.set_exception(RuntimeError(error))
        else:
            future.set_result(value)

    async def _read(self) -> None:
        assert self._proc and self._proc.stdout
        async for raw in self._proc.stdout:
            message = json.loads(raw)
            match message["type"]:
                case "loaded":
                    self._settle_once("loaded", None, message["manifest"])
                case "load-failed":
                    self._settle_once("loaded", message["error"], None)
                case "started":
                    self._settle_once("started", message.get("error"), None)
                case "response":
                    self._settle(message["id"], message.get("error"), message.get("res") or {})
                case "delivered":
                    self._settle(message["id"], message.get("error"), None)
                case "call":
                    task = asyncio.create_task(self._answer(message))
                    self._calls.add(task)
                    task.add_done_callback(self._calls.discard)
                case "log":
                    getattr(self.log, message["level"], self.log.info)(message["message"], message.get("data"))
        # stdout closed: the process is gone
        await self._proc.wait()
        for future in [*self._waiting.values(), *self._once.values()]:
            if not future.done():
                future.set_exception(QuanStopped(f"{self.source.name} exited"))
        for listener in self.on_exit:
            listener(self._proc.returncode)

    async def _answer(self, message: dict[str, Any]) -> None:
        capability = self.capabilities.get(message["capability"])
        if capability is None:
            self._send({"type": "result", "id": message["id"], "error": f"{message['capability']} is not plugged into {self.source.name}"})
            return
        try:
            self._send({"type": "result", "id": message["id"], "value": await capability(*message["args"])})
        except Exception as error:  # the quan gets the message, the quanar keeps running
            self._send({"type": "result", "id": message["id"], "error": str(error)})
