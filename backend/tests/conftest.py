"""Generic fixtures shared across all backend tests."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Register all SQLModel table models with the shared metadata before any test runs.
from app.auth.infrastructure.db import models as _auth_models  # noqa: F401

TEST_DATABASE_URL = (
    "postgresql+asyncpg://monopoly:monopoly@localhost:5434/monopoly_test"
)


# ---------------------------------------------------------------------------
# RSA key pair — generated once per test session
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def test_rsa_keys() -> tuple[str, str]:
    """Return a (private_pem, public_pem) pair used by all tests in the session."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


# ---------------------------------------------------------------------------
# Database engine + schema lifecycle — session-scoped
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create an async engine for the test database.

    Tables are created once before the first test and dropped after the last.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


# ---------------------------------------------------------------------------
# Per-test transactional session — rolls back after each test
# ---------------------------------------------------------------------------


@pytest.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an AsyncSession scoped to a single test.

    All writes are flushed to the database within the open transaction so
    subsequent queries within the same test can see the data.  The transaction
    is rolled back unconditionally when the test finishes, keeping tests fully
    isolated from one another.
    """
    async with test_engine.connect() as conn:
        await conn.begin()
        async with AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        ) as session:
            yield session
        await conn.rollback()


# ---------------------------------------------------------------------------
# FastAPI app with get_session overridden — runs automatically for every test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
async def test_app(db_session: AsyncSession) -> AsyncGenerator[Any, None]:
    """Override the database session for the duration of every test.

    Replaces ``get_session`` with the function-scoped ``db_session`` so every
    HTTP request through the app participates in the same rolled-back
    transaction as the test itself.  Yielding the app lets tests that need the
    FastAPI instance (e.g. to build an AsyncClient) request this fixture by
    name.
    """
    from app.main import app
    from app.auth.infrastructure.db.postgres import get_session

    async def _override_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = _override_session
    yield app
    app.dependency_overrides.clear()
