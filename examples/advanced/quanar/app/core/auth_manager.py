"""Identity, without knowing any user. A quan proves who someone is however it likes and asks
for a token; the quanar signs it and, on every request, reads it back."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import secrets
import time
from datetime import UTC, datetime

from shop_qua import AuthUser, IssuedToken, TokenClaims

from ..config import settings
from .logger import get_logger

log = get_logger("auth")

_secret = (settings.jwt_secret or secrets.token_hex(32)).encode()
if not settings.jwt_secret:
    log.warn("JWT_SECRET is not set: a random secret is used and tokens will not survive a restart")

_HEADER = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b"=").decode()
# scrypt's cost: about 50 ms and 16 MB per password.
_N, _R, _P, _LENGTH = 2**14, 8, 1, 64


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sign(data: str) -> str:
    return _b64(hmac.new(_secret, data.encode(), hashlib.sha256).digest())


def issue_token(claims: TokenClaims) -> IssuedToken:
    issued = int(time.time())
    expires = issued + settings.token_ttl_seconds
    payload = {"sub": claims["sub"], "name": claims["name"], "permissions": list(claims["permissions"]), "iat": issued, "exp": expires}
    body = f"{_HEADER}.{_b64(json.dumps(payload).encode())}"
    return {"token": f"{body}.{_sign(body)}", "expires_at": datetime.fromtimestamp(expires, UTC).isoformat().replace("+00:00", "Z")}


def verify_token(token: str) -> AuthUser | None:
    """The user behind a token, or None when it is missing, forged or expired."""
    parts = token.split(".")
    if len(parts) != 3 or not hmac.compare_digest(_sign(f"{parts[0]}.{parts[1]}"), parts[2]):
        return None
    try:
        claims = json.loads(_unb64(parts[1]))
    except ValueError:
        return None
    if not isinstance(claims, dict) or claims.get("exp", 0) < time.time():
        return None
    return {"id": str(claims["sub"]), "name": claims.get("name"), "permissions": list(claims.get("permissions", []))}


def _scrypt(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=_LENGTH)


async def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = await asyncio.to_thread(_scrypt, password, salt)
    return f"scrypt${salt.hex()}${digest.hex()}"


async def verify_password(password: str, stored: str) -> bool:
    scheme, _, rest = stored.partition("$")
    salt_hex, _, digest_hex = rest.partition("$")
    if scheme != "scrypt" or not salt_hex or not digest_hex:
        return False
    digest = await asyncio.to_thread(_scrypt, password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(digest, bytes.fromhex(digest_hex))
