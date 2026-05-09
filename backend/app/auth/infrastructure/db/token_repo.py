"""SQLModel implementation of TokenRepository."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.domain.models import RefreshToken
from app.auth.infrastructure.db.models import RefreshTokenTable


def _to_domain(row: RefreshTokenTable) -> RefreshToken:
    return RefreshToken(
        token_hash=row.token_hash,
        user_id=row.user_id,
        expires_at=row.expires_at,
        revoked_at=row.revoked_at,
        device_hint=row.device_hint,
        created_at=row.created_at,
    )


class SQLTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_refresh_token(
        self,
        *,
        token_hash: str,
        user_id: UUID,
        expires_at: datetime,
        device_hint: str | None,
    ) -> RefreshToken:
        row = RefreshTokenTable(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
            device_hint=device_hint,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return _to_domain(row)

    async def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        row = await self._session.get(RefreshTokenTable, token_hash)
        return _to_domain(row) if row else None

    async def revoke_refresh_token(self, token_hash: str) -> None:
        row = await self._session.get(RefreshTokenTable, token_hash)
        if row:
            row.revoked_at = datetime.now(timezone.utc)
            self._session.add(row)
            await self._session.flush()

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        result = await self._session.exec(
            select(RefreshTokenTable).where(
                RefreshTokenTable.user_id == user_id,
                col(RefreshTokenTable.revoked_at).is_(None),
            )
        )
        now = datetime.now(timezone.utc)
        for row in result.all():
            row.revoked_at = now
            self._session.add(row)
        await self._session.flush()
