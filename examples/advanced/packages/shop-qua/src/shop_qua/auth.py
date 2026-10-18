"""Identity work the quanar does for a quan: hashing, checking and signing never leave the quanar."""

from __future__ import annotations

from .state import get_quanar_core
from .types import IssuedToken, TokenClaims


async def issue_token(claims: TokenClaims) -> IssuedToken:
    return await get_quanar_core().auth.issue_token(claims)


async def hash_password(password: str) -> str:
    return await get_quanar_core().auth.hash_password(password)


async def verify_password(password: str, hashed: str) -> bool:
    return await get_quanar_core().auth.verify_password(password, hashed)
