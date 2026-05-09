"""RS256 implementations of JWTSigner and JWTVerifier.

Uses pyjwt[crypto] under the hood. The signer holds the private key
(auth service only); the verifier holds only the public key (any service).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.config import settings


class RS256Signer:
    """Signs JWTs with the RS256 private key."""

    def __init__(self, private_key_pem: str, expire_minutes: int) -> None:
        self._private_key = private_key_pem
        self._expire_minutes = expire_minutes

    def sign(self, payload: dict[str, Any]) -> str:
        now = datetime.now(timezone.utc)
        claims = {
            **payload,
            "iat": now,
            "exp": now + timedelta(minutes=self._expire_minutes),
        }
        return jwt.encode(claims, self._private_key, algorithm="RS256")


class RS256Verifier:
    """Verifies JWTs with the RS256 public key.

    Can be used by any service — the public key is non-sensitive.
    """

    def __init__(self, public_key_pem: str) -> None:
        self._public_key = public_key_pem

    def verify(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self._public_key, algorithms=["RS256"])
        except jwt.ExpiredSignatureError as exc:
            raise ValueError("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise ValueError(f"Invalid token: {exc}") from exc


def make_signer() -> RS256Signer:
    return RS256Signer(
        private_key_pem=settings.jwt_private_key_pem,
        expire_minutes=settings.access_token_expire_minutes,
    )


def make_verifier() -> RS256Verifier:
    return RS256Verifier(public_key_pem=settings.jwt_public_key_pem)
