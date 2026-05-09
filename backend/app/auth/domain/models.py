from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(frozen=True)


class User(Base):
    id: UUID
    email: str
    hashed_password: str | None
    display_name: str
    created_at: datetime


class OAuthAccount(Base):
    id: UUID
    user_id: UUID
    provider: str
    provider_user_id: str


class RefreshToken(Base):
    token_hash: str
    user_id: UUID
    expires_at: datetime
    revoked_at: datetime | None
    device_hint: str | None
    created_at: datetime

    @property
    def is_valid(self) -> bool:
        return self.revoked_at is None and datetime.now(timezone.utc) < self.expires_at
