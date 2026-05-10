"""SQLModel table models for auth.

These are infrastructure-only — never imported by domain or application layers.
Domain ↔ infrastructure mapping is done explicitly in the repository impls.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, DateTime, Column


class UserTable(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str | None = Field(default=None)
    display_name: str = Field(max_length=100)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )


class OAuthAccountTable(SQLModel, table=True):
    __tablename__ = "oauth_accounts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    provider: str = Field(max_length=32)
    provider_user_id: str = Field(max_length=255)


class RefreshTokenTable(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    token_hash: str = Field(primary_key=True, max_length=64)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    revoked_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    device_hint: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
