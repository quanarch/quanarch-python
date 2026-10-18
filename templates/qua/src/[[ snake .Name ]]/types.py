"""The shapes the quanar and its quans agree on."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Literal, Protocol, TypedDict

HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
Row = dict[str, Any]


class Request(TypedDict):
    """A request as a quan sees it. The quanar's HTTP server never reaches the quan."""

    method: HttpMethod
    path: str
    params: dict[str, str]
    query: dict[str, str]
    headers: dict[str, str]
    body: Any


class Response(TypedDict, total=False):
    status: int
    body: Any


Handler = Callable[[Request], Awaitable[Response]]


class ApiManager(Protocol):
    """The quanar's listener. api.get("/items", handler) asks the quanar to listen for the quan."""

    def get(self, path: str, handler: Handler) -> None: ...
    def post(self, path: str, handler: Handler) -> None: ...
    def put(self, path: str, handler: Handler) -> None: ...
    def patch(self, path: str, handler: Handler) -> None: ...
    def delete(self, path: str, handler: Handler) -> None: ...


class DbManager(Protocol):
    """The quanar's database. General methods only: the quan names the table."""

    async def create(self, table: str, data: dict[str, Any]) -> Row: ...
    async def list(self, table: str) -> list[Row]: ...
    async def get(self, table: str, id: str) -> Row | None: ...
    async def update(self, table: str, id: str, data: dict[str, Any]) -> Row | None: ...
    async def remove(self, table: str, id: str) -> bool: ...


class QuanarCore(Protocol):
    """What the quanar implements and plugs in with init()."""

    @property
    def api(self) -> ApiManager: ...

    @property
    def db(self) -> DbManager: ...
