"""Settings of the quanar, and the list of quans it loads."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class QuanSource:
    """Where a quan lives and which quas are plugged into it."""

    name: str
    url: str
    version: str = ""
    #: An event stream that announces a new build with a change event.
    events: str | None = None
    #: SHA-256 of the file. When set, a file that does not match never runs.
    hash: str | None = None
    quas: tuple[str, ...] = ()


def _path(variable: str, default: Path) -> Path:
    return Path(os.environ[variable]) if variable in os.environ else default


@dataclass(frozen=True)
class Settings:
    port: int = int(os.environ.get("PORT", "3000"))
    #: Where the quans are listed: name, file, hash, event stream, quas. Written by the build.
    quans_file: Path = _path("QUANS_FILE", ROOT / "data" / "quans.json")
    database_file: Path = _path("DATABASE_FILE", ROOT / "data" / "shop.db")
    #: Signs the tokens. Without it a random one is made, and tokens do not survive a restart.
    jwt_secret: str | None = os.environ.get("JWT_SECRET")
    token_ttl_seconds: int = int(os.environ.get("TOKEN_TTL_SECONDS", str(8 * 60 * 60)))
    rate_limit_window_seconds: float = 60.0
    rate_limit_max: int = int(os.environ.get("RATE_LIMIT_MAX", "30"))
    body_limit_bytes: int = 100 * 1024
    reconnect_seconds: float = 2.0
    fetch_timeout_seconds: float = 3.0
    load_timeout_seconds: float = 5.0
    request_timeout_seconds: float = 10.0
    #: How long a quan waits for the quanar to answer one of its calls.
    call_timeout_seconds: float = 5.0
    quan_memory_mb: int = 256


settings = Settings()


def read_quan_sources() -> list[QuanSource]:
    """The quans this quanar loads. The list lives outside the code, in data/quans.json."""
    try:
        listed = json.loads(settings.quans_file.read_text())
    except (OSError, ValueError):
        return []
    return [
        QuanSource(
            name=q["name"],
            url=q["url"],
            version=q.get("version", ""),
            events=q.get("events"),
            hash=q.get("hash"),
            quas=tuple(q.get("quas", ())),
        )
        for q in listed
    ]
