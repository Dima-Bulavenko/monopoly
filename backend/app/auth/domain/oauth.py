"""OAuth provider Protocol and value objects for the auth domain.

No imports from infrastructure — concrete impls live in
app/auth/infrastructure/oauth/.
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict


class OAuthIdentity(BaseModel):
    """Normalised identity returned by any OAuth provider."""

    model_config = ConfigDict(frozen=True)

    provider: str
    provider_user_id: str
    email: str
    display_name: str


class IOAuthProvider(Protocol):
    async def verify_id_token(self, id_token: str) -> OAuthIdentity:
        """Verify the provider-issued ID token and return a normalised identity.

        Raises ValueError on invalid / expired tokens.
        """
        ...
