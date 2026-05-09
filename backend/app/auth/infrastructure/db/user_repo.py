"""SQLModel implementation of UserRepository."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.domain.models import OAuthAccount, User
from app.auth.infrastructure.db.models import OAuthAccountTable, UserTable


def _to_user(row: UserTable) -> User:
    return User(
        id=row.id,
        email=row.email,
        hashed_password=row.hashed_password,
        display_name=row.display_name,
        created_at=row.created_at,
    )


def _to_oauth(row: OAuthAccountTable) -> OAuthAccount:
    return OAuthAccount(
        id=row.id,
        user_id=row.user_id,
        provider=row.provider,
        provider_user_id=row.provider_user_id,
    )


class SQLUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        row = await self._session.get(UserTable, user_id)
        return _to_user(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.exec(
            select(UserTable).where(UserTable.email == email)
        )
        row = result.first()
        return _to_user(row) if row else None

    async def create(
        self,
        *,
        email: str,
        hashed_password: str | None,
        display_name: str,
    ) -> User:
        row = UserTable(
            email=email,
            hashed_password=hashed_password,
            display_name=display_name,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return _to_user(row)

    async def get_oauth_account(
        self,
        provider: str,
        provider_user_id: str,
    ) -> OAuthAccount | None:
        result = await self._session.exec(
            select(OAuthAccountTable).where(
                OAuthAccountTable.provider == provider,
                OAuthAccountTable.provider_user_id == provider_user_id,
            )
        )
        row = result.first()
        return _to_oauth(row) if row else None

    async def upsert_oauth_account(
        self,
        *,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
    ) -> OAuthAccount:
        result = await self._session.exec(
            select(OAuthAccountTable).where(
                OAuthAccountTable.provider == provider,
                OAuthAccountTable.provider_user_id == provider_user_id,
            )
        )
        row = result.first()
        if row is None:
            row = OAuthAccountTable(
                id=uuid4(),
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_user_id,
            )
            self._session.add(row)
            await self._session.flush()
            await self._session.refresh(row)
        return _to_oauth(row)
