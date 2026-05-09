"""Google OAuthProvider implementation using google-auth."""

from __future__ import annotations

import asyncio

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.auth.domain.oauth import OAuthIdentity


class GoogleOAuthProvider:
    def __init__(self, client_id: str) -> None:
        self._client_id = client_id

    async def verify_id_token(self, id_token: str) -> OAuthIdentity:
        # google-auth is sync; run in thread pool to stay async-safe
        loop = asyncio.get_running_loop()
        try:
            idinfo = await loop.run_in_executor(
                None,
                self._verify_sync,
                id_token,
            )
        except ValueError as exc:
            raise ValueError(f"Invalid Google ID token: {exc}") from exc

        return OAuthIdentity(
            provider="google",
            provider_user_id=idinfo["sub"],
            email=idinfo["email"],
            display_name=idinfo.get("name", idinfo["email"]),
        )

    def _verify_sync(self, id_token: str) -> dict:
        request = google_requests.Request()
        return google_id_token.verify_oauth2_token(id_token, request, self._client_id)
