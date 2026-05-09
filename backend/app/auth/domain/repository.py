"""Repository Protocols for the auth domain.

These are abstract contracts — no imports from infrastructure.
Concrete implementations live in app/auth/infrastructure/db/.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.auth.domain.models import OAuthAccount, RefreshToken, User


class UserRepository(Protocol):
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def create(
        self,
        *,
        email: str,
        hashed_password: str | None,
        display_name: str,
    ) -> User: ...

    async def get_oauth_account(
        self,
        provider: str,
        provider_user_id: str,
    ) -> OAuthAccount | None: ...

    async def upsert_oauth_account(
        self,
        *,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
    ) -> OAuthAccount: ...


class TokenRepository(Protocol):
    async def create_refresh_token(
        self,
        *,
        token_hash: str,
        user_id: UUID,
        expires_at: datetime,
        device_hint: str | None,
    ) -> RefreshToken: ...

    async def get_refresh_token(self, token_hash: str) -> RefreshToken | None: ...

    async def revoke_refresh_token(self, token_hash: str) -> None: ...

    async def revoke_all_for_user(self, user_id: UUID) -> None: ...
