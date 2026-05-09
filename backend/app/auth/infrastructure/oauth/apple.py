"""Apple Sign-In OAuthProvider implementation.

Verifies Apple ID tokens by fetching Apple's public JWKS and validating
with pyjwt[crypto].  This covers the iOS client flow.

Note: the Android / web server-side authorization-code flow requires
a separate code-exchange step not implemented here.
"""

from __future__ import annotations

from typing import Any

import httpx
import jwt
from jwt.algorithms import RSAAlgorithm

from app.auth.domain.oauth import OAuthIdentity

_APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
_APPLE_ISSUER = "https://appleid.apple.com"


class AppleOAuthProvider:
    def __init__(self, client_id: str) -> None:
        self._client_id = client_id

    async def verify_id_token(self, id_token: str) -> OAuthIdentity:
        jwks = await self._fetch_jwks()

        # Decode header without verification to find the right key
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")

        public_key = self._find_key(jwks, kid)

        try:
            payload = jwt.decode(
                id_token,
                public_key,
                algorithms=["RS256"],
                audience=self._client_id,
                issuer=_APPLE_ISSUER,
            )
        except jwt.ExpiredSignatureError as exc:
            raise ValueError("Apple ID token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise ValueError(f"Invalid Apple ID token: {exc}") from exc

        return OAuthIdentity(
            provider="apple",
            provider_user_id=payload["sub"],
            email=payload.get("email", ""),
            display_name=payload.get("name", payload.get("email", "")),
        )

    async def _fetch_jwks(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(_APPLE_JWKS_URL)
            resp.raise_for_status()
            return resp.json()

    def _find_key(self, jwks: dict, kid: str | None) -> Any:
        for key_data in jwks.get("keys", []):
            if kid is None or key_data.get("kid") == kid:
                return RSAAlgorithm.from_jwk(key_data)
        raise ValueError(f"Apple public key not found for kid={kid!r}")
