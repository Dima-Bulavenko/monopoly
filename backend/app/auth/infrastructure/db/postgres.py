"""Async SQLModel engine factory and session dependency."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.is_local,
            pool_pre_ping=True,
        )
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(get_engine(), expire_on_commit=False) as session:
        yield session
        await session.commit()
