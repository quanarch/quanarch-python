"""One quan in its own process. The quanar talks to it only through JSON lines."""

from __future__ import annotations

import asyncio
import base64
import itertools
import json
import sys
from pathlib import Path
from typing import Any

from ..config import QuanSource, settings
from .logger import get_logger
from .qua_core import plugged

HOST = Path(__file__).resolve().parent.parent / "quan_host.py"


class QuanStopped(Exception):
    pass


class QuanProcess:
    def __init__(self, source: QuanSource) -> None:
        self.source = source
        self.log = get_logger(source.name)
        self.capabilities = plugged(source.quas)
        self._ids = itertools.count(1)
        self._waiting: dict[int, asyncio.Future[Any]] = {}
        self._loaded: asyncio.Future[list[dict[str, str]]] | None = None
        self.proc: asyncio.subprocess.Process | None = None
        self._reader: asyncio.Task[None] | None = None
        self.on_exit: list[Any] = []

    @property
    def pid(self) -> int | None:
        return self.proc.pid if self.proc else None

    async def start(self, code: bytes) -> list[dict[str, str]]:
        """Starts the quan's process, sends the code in, waits for what it asked to listen to."""
        # The host sets its own memory ceiling and call timeout as it starts, before any quan code arrives.
        self.proc = await asyncio.create_subprocess_exec(
            sys.executable, "-I", str(HOST),
            "--memory-mb", str(settings.quan_memory_mb),
            "--call-timeout", str(settings.call_timeout_seconds),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            env={},  # no secrets, no addresses, nothing of the quanar's
            limit=16 * 1024 * 1024,
        )
        self._reader = asyncio.create_task(self._read())
        self._loaded = asyncio.get_running_loop().create_future()
        self._send({"type": "load", "name": self.source.name, "code": base64.b64encode(code).decode(), "quas": list(self.source.quas)})
        try:
            return await asyncio.wait_for(self._loaded, settings.load_timeout_seconds)
        except BaseException:
            self.kill()
            raise

    async def request(self, listener: int, req: dict[str, Any]) -> dict[str, Any]:
        id_ = next(self._ids)
        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self._waiting[id_] = future
        self._send({"type": "request", "id": id_, "listener": listener, "req": req})
        try:
            return await asyncio.wait_for(future, settings.request_timeout_seconds)
        except asyncio.TimeoutError:
            # A quan stuck in a loop is shut down; its process goes, the quanar stays.
            self.log.error("no answer in %ss, stopping it", settings.request_timeout_seconds)
            self.kill()
            return {"status": 504, "body": {"error": f"{self.source.name} did not answer"}}
        except QuanStopped:
            return {"status": 503, "body": {"error": f"{self.source.name} stopped"}}
        finally:
            self._waiting.pop(id_, None)

    async def stop(self) -> None:
        if not self.proc or self.proc.returncode is not None:
            return
        self._send({"type": "unmount"})
        try:
            await asyncio.wait_for(self.proc.wait(), 2)
        except asyncio.TimeoutError:
            self.kill()

    def kill(self) -> None:
        if self.proc and self.proc.returncode is None:
            self.proc.kill()

    def _send(self, message: dict[str, Any]) -> None:
        if self.proc and self.proc.stdin and not self.proc.stdin.is_closing():
            self.proc.stdin.write((json.dumps(message) + "\n").encode())

    async def _read(self) -> None:
        assert self.proc and self.proc.stdout
        async for raw in self.proc.stdout:
            message = json.loads(raw)
            kind = message["type"]
            if kind == "loaded" and self._loaded and not self._loaded.done():
                self._loaded.set_result(message["listens"])
            elif kind == "load-failed" and self._loaded and not self._loaded.done():
                self._loaded.set_exception(RuntimeError(message["error"]))
            elif kind == "response":
                future = self._waiting.get(message["id"])
                if future and not future.done():
                    if "error" in message:
                        future.set_result({"status": 500, "body": {"error": "The quan failed"}})
                        self.log.error("%s", message["error"])
                    else:
                        future.set_result(message["res"])
            elif kind == "call":
                asyncio.create_task(self._answer(message))
            elif kind == "log":
                getattr(self.log, message["level"], self.log.info)("%s", message["message"])
        # stdout closed: the process is gone
        await self.proc.wait()
        for future in self._waiting.values():
            if not future.done():
                future.set_exception(QuanStopped())
        if self._loaded and not self._loaded.done():
            self._loaded.set_exception(RuntimeError(f"{self.source.name} exited while loading"))
        for listener in self.on_exit:
            listener(self.proc.returncode)

    async def _answer(self, message: dict[str, Any]) -> None:
        capability = self.capabilities.get(message["capability"])
        if capability is None:
            self._send({"type": "result", "id": message["id"], "error": f"{message['capability']} is not plugged into {self.source.name}"})
            return
        try:
            self._send({"type": "result", "id": message["id"], "value": await capability(*message["args"])})
        except Exception as error:  # the quan gets the message, the quanar keeps running
            self._send({"type": "result", "id": message["id"], "error": str(error)})
