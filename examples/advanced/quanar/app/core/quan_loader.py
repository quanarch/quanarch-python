"""Downloads a quan's file and checks it. Nothing runs here."""

from __future__ import annotations

import httpx

from ..config import QuanSource, settings
from ..utils import sha256_hex


class UnreachableError(Exception):
    pass


class HashMismatchError(Exception):
    pass


async def fetch(source: QuanSource) -> bytes:
    try:
        async with httpx.AsyncClient(timeout=settings.fetch_timeout_seconds) as client:
            response = await client.get(source.url, headers={"Cache-Control": "no-store"})
    except httpx.HTTPError as error:
        raise UnreachableError(f"{source.url} could not be reached") from error
    if response.status_code != 200:
        raise UnreachableError(f"{source.url} answered {response.status_code}")
    return response.content


def verify(source: QuanSource, code: bytes) -> str:
    """Returns the file's hash; raises when the list expects another one."""
    actual = sha256_hex(code)
    if source.hash and actual != source.hash:
        raise HashMismatchError(f"expected {source.hash[:12]}…, got {actual[:12]}…")
    return actual
