"""Tests for POST /auth/refresh."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

ENDPOINT = "/auth/refresh"
_COOKIE_NAME = "refresh_token"


@pytest.fixture
async def http_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
async def refresh_response(
    http_client: AsyncClient,
    registered_user: dict[str, Any],
):
    """POST /auth/refresh with the registered user's refresh token cookie."""
    return await http_client.post(
        ENDPOINT,
        headers={"Cookie": f"{_COOKIE_NAME}={registered_user['refresh_token']}"},
    )


# ---------------------------------------------------------------------------
# Happy-path tests (200 OK)
# ---------------------------------------------------------------------------


async def test_refresh_returns_200(refresh_response):
    assert refresh_response.status_code == 200


async def test_refresh_body_has_access_token(refresh_response):
    body = refresh_response.json()
    assert "access_token" in body
    assert body["access_token"]


async def test_refresh_token_type_is_bearer(refresh_response):
    assert refresh_response.json()["token_type"] == "bearer"


async def test_refresh_sets_new_refresh_cookie(refresh_response):
    assert _COOKIE_NAME in refresh_response.cookies


async def test_refresh_cookie_is_httponly(refresh_response):
    set_cookie = refresh_response.headers.get("set-cookie", "")
    assert "httponly" in set_cookie.lower()


async def test_refresh_cookie_path_is_auth(refresh_response):
    set_cookie = refresh_response.headers.get("set-cookie", "")
    assert "path=/auth" in set_cookie.lower()


# ---------------------------------------------------------------------------
# Token rotation — old token is revoked after a successful refresh
# ---------------------------------------------------------------------------


async def test_refresh_old_token_is_revoked_after_rotation(
    http_client: AsyncClient,
    registered_user: dict[str, Any],
):
    first_refresh = registered_user["refresh_token"]

    # Consume the first refresh token
    await http_client.post(
        ENDPOINT, headers={"Cookie": f"{_COOKIE_NAME}={first_refresh}"}
    )

    # Using the old token again must fail
    response = await http_client.post(
        ENDPOINT, headers={"Cookie": f"{_COOKIE_NAME}={first_refresh}"}
    )
    assert response.status_code == 401


async def test_refresh_new_token_is_valid_after_rotation(
    http_client: AsyncClient,
    registered_user: dict[str, Any],
):
    first_response = await http_client.post(
        ENDPOINT,
        headers={"Cookie": f"{_COOKIE_NAME}={registered_user['refresh_token']}"},
    )
    new_token = first_response.cookies[_COOKIE_NAME]

    # New token must be usable
    second_response = await http_client.post(
        ENDPOINT,
        headers={"Cookie": f"{_COOKIE_NAME}={new_token}"},
    )
    assert second_response.status_code == 200


# ---------------------------------------------------------------------------
# Error tests (401 Unauthorized)
# ---------------------------------------------------------------------------


async def test_refresh_without_cookie_returns_401(http_client: AsyncClient):
    response = await http_client.post(ENDPOINT)
    assert response.status_code == 401


async def test_refresh_without_cookie_response_has_detail(http_client: AsyncClient):
    response = await http_client.post(ENDPOINT)
    assert "detail" in response.json()


async def test_refresh_with_invalid_token_returns_401(http_client: AsyncClient):
    response = await http_client.post(
        ENDPOINT,
        headers={"Cookie": f"{_COOKIE_NAME}=completely-invalid-token"},
    )
    assert response.status_code == 401
