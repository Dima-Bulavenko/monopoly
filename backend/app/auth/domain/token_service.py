"""Token and password service Protocols for the auth domain.

No imports from infrastructure — concrete impls live in
app/auth/infrastructure/jwt/ and app/auth/infrastructure/password/.
"""

from __future__ import annotations

from typing import Any, Protocol


class JWTSigner(Protocol):
    def sign(self, payload: dict[str, Any]) -> str:
        """Sign a payload and return a JWT string."""
        ...


class JWTVerifier(Protocol):
    def verify(self, token: str) -> dict[str, Any]:
        """Verify a JWT and return its decoded payload.

        Raises ValueError on invalid / expired tokens.
        """
        ...


class PasswordHasher(Protocol):
    def hash(self, plain: str) -> str:
        """Hash a plain-text password."""
        ...

    def verify(self, plain: str, hashed: str) -> bool:
        """Return True if *plain* matches *hashed*."""
        ...
