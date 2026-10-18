"""What crosses between a quan and the quanar while it runs, and the core the quanar plugs in."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Literal, NotRequired, Protocol, TypedDict

# ---- who is calling ----


class AuthUser(TypedDict):
    """Who is calling, as the quanar read it from the request's token."""

    #: The subject the token was issued for, usually a user id.
    id: str
    name: str | None
    permissions: list[str]


class TokenClaims(TypedDict):
    """What a quan asks the quanar to put in a token."""

    sub: str
    name: str | None
    permissions: list[str]


class IssuedToken(TypedDict):
    token: str
    #: ISO time
    expires_at: str


# ---- a request ----


class ApiRequest(TypedDict):
    """A request as the quan sees it: already authenticated, permitted and validated by the quanar."""

    request_id: str
    method: str
    path: str
    params: dict[str, Any]
    query: dict[str, Any]
    headers: dict[str, str]
    body: Any
    user: AuthUser | None
    #: Filled by the quan's own middlewares for the handler that follows, for example a loaded row.
    locals: dict[str, Any]


class ApiResponse(TypedDict, total=False):
    status: int
    body: Any
    headers: dict[str, str]


Handler = Callable[[ApiRequest], Awaitable[ApiResponse]]
Next = Callable[[], Awaitable[ApiResponse]]
#: A middleware of the quan itself. It runs in the quan, after the quanar's checks.
LocalMiddleware = Callable[[ApiRequest, Next], Awaitable[ApiResponse]]


class ValidationIssue(TypedDict):
    """A failed rule, as the quanar answers it with 422."""

    path: str
    message: str


# ---- events ----


class EventMeta(TypedDict):
    #: The quan that emitted it.
    emitted_by: str
    #: ISO time
    at: str


EventHandler = Callable[[Any, EventMeta], Awaitable[None]]


# ---- the database, as operations ----

#: A row as the quanar returns it: the quan's fields, with id, created_at and updated_at.
Row = dict[str, Any]
#: Field → value, or field → {"eq" | "ne" | "gt" | "gte" | "lt" | "lte" | "in" | "like": value}.
Where = Mapping[str, Any]
Order = Literal["asc", "desc"]


class DbOperation(TypedDict):
    """One database operation, as data: it crosses from the quan's process to the quanar."""

    action: Literal["find", "find_one", "count", "create", "update", "delete"]
    model: str
    where: NotRequired[Where]
    order_by: NotRequired[Mapping[str, Order]]
    limit: NotRequired[int]
    offset: NotRequired[int]
    #: For create and update. A number may change in place: {"stock": {"decrement": 2}}.
    data: NotRequired[Mapping[str, Any]]
    #: For update and delete: any other number of rows fails the operation, and its transaction.
    expect: NotRequired[int]


# ---- the core the quanar plugs in ----


class DbCapability(Protocol):
    """The quanar's database, seen through a quan: only that quan's models exist."""

    async def run(self, operation: DbOperation) -> Any: ...

    async def transaction(self, operations: list[DbOperation]) -> list[Any]:
        """Runs every operation or none."""
        ...


class AuthCapability(Protocol):
    """Identity work the quanar does: signing and checking secrets never leave it."""

    async def issue_token(self, claims: TokenClaims) -> IssuedToken: ...
    async def hash_password(self, password: str) -> str: ...
    async def verify_password(self, password: str, hashed: str) -> bool: ...


class EventsCapability(Protocol):
    async def emit(self, event: str, payload: Any) -> None:
        """The name must start with the emitting quan's name."""
        ...


class Logger(Protocol):
    def info(self, message: str, data: Any = None) -> None: ...
    def warn(self, message: str, data: Any = None) -> None: ...
    def error(self, message: str, data: Any = None) -> None: ...


class QuanarCore(Protocol):
    """What the quanar implements and plugs in with init()."""

    @property
    def db(self) -> DbCapability: ...

    @property
    def auth(self) -> AuthCapability: ...

    @property
    def events(self) -> EventsCapability: ...

    @property
    def log(self) -> Logger: ...
