"""Tests for POST /auth/logout."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

ENDPOINT = "/auth/logout"
_COOKIE_NAME = "refresh_token"
_REFRESH_ENDPOINT = "/auth/refresh"


@pytest.fixture
async def http_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Happy-path tests (204 No Content)
# ---------------------------------------------------------------------------


async def test_logout_with_cookie_returns_204(
    http_client: AsyncClient,
    registered_user: dict[str, Any],
):
    response = await http_client.post(
        ENDPOINT,
        headers={"Cookie": f"{_COOKIE_NAME}={registered_user['refresh_token']}"},
    )
    assert response.status_code == 204


async def test_logout_without_cookie_returns_204(http_client: AsyncClient):
    # Logout must be idempotent — no cookie is not an error
    response = await http_client.post(ENDPOINT)
    assert response.status_code == 204


# ---------------------------------------------------------------------------
# Cookie clearing
# ---------------------------------------------------------------------------


async def test_logout_clears_refresh_cookie(
    http_client: AsyncClient,
    registered_user: dict[str, Any],
):
    response = await http_client.post(
        ENDPOINT,
        headers={"Cookie": f"{_COOKIE_NAME}={registered_user['refresh_token']}"},
    )
    set_cookie = response.headers.get("set-cookie", "")
    # FastAPI's delete_cookie sets max-age=0
    assert "max-age=0" in set_cookie.lower()


# ---------------------------------------------------------------------------
# Token revocation — refresh token must be unusable after logout
# ---------------------------------------------------------------------------


async def test_logout_revokes_refresh_token(
    http_client: AsyncClient,
    registered_user: dict[str, Any],
):
    refresh_token = registered_user["refresh_token"]

    await http_client.post(
        ENDPOINT, headers={"Cookie": f"{_COOKIE_NAME}={refresh_token}"}
    )

    # Attempting to use the revoked token must fail
    response = await http_client.post(
        _REFRESH_ENDPOINT,
        headers={"Cookie": f"{_COOKIE_NAME}={refresh_token}"},
    )
    assert response.status_code == 401
