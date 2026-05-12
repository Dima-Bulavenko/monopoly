"""Tests for POST /auth/apple."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture

from app.auth.domain.oauth import OAuthIdentity

ENDPOINT = "/auth/apple"
_PROVIDER_PATH = "app.auth.api.router.get_apple_provider"


@pytest.fixture
async def http_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def apple_identity() -> OAuthIdentity:
    """A valid OAuthIdentity as returned by the Apple provider."""
    return OAuthIdentity(
        provider="apple",
        provider_user_id="apple-uid-001",
        email="appleuser@example.com",
        display_name="Apple User",
    )


@pytest.fixture
def mock_apple_provider(
    mocker: MockerFixture, apple_identity: OAuthIdentity
) -> AsyncMock:
    """Patch get_apple_provider to return a mock that verifies any id_token."""
    provider = AsyncMock()
    provider.verify_id_token.return_value = apple_identity
    mocker.patch(_PROVIDER_PATH, return_value=provider)
    return provider


@pytest.fixture
def make_apple_body() -> Any:
    def factory(**overrides: Any) -> dict[str, Any]:
        return {"id_token": "valid-apple-id-token", **overrides}

    return factory


# ---------------------------------------------------------------------------
# Happy-path tests (200 OK)
# ---------------------------------------------------------------------------


async def test_login_apple_returns_200(
    http_client: AsyncClient,
    make_apple_body: Any,
    mock_apple_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json=make_apple_body())
    assert response.status_code == 200


async def test_login_apple_body_has_access_token(
    http_client: AsyncClient,
    make_apple_body: Any,
    mock_apple_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json=make_apple_body())
    body = response.json()
    assert "access_token" in body
    assert body["access_token"]


async def test_login_apple_token_type_is_bearer(
    http_client: AsyncClient,
    make_apple_body: Any,
    mock_apple_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json=make_apple_body())
    assert response.json()["token_type"] == "bearer"


async def test_login_apple_sets_refresh_token_cookie(
    http_client: AsyncClient,
    make_apple_body: Any,
    mock_apple_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json=make_apple_body())
    assert "refresh_token" in response.cookies


async def test_login_apple_same_identity_reuses_existing_user(
    http_client: AsyncClient,
    make_apple_body: Any,
    mock_apple_provider: AsyncMock,
):
    # Two logins with the same Apple identity must both succeed
    first = await http_client.post(ENDPOINT, json=make_apple_body())
    second = await http_client.post(ENDPOINT, json=make_apple_body())
    assert first.status_code == 200
    assert second.status_code == 200


# ---------------------------------------------------------------------------
# Error tests (401 Unauthorized)
# ---------------------------------------------------------------------------


async def test_login_apple_invalid_token_returns_401(
    http_client: AsyncClient,
    make_apple_body: Any,
    mocker: MockerFixture,
):
    provider = AsyncMock()
    provider.verify_id_token.side_effect = ValueError("invalid token")
    mocker.patch(_PROVIDER_PATH, return_value=provider)

    response = await http_client.post(ENDPOINT, json=make_apple_body())
    assert response.status_code == 401


async def test_login_apple_invalid_token_response_has_detail(
    http_client: AsyncClient,
    make_apple_body: Any,
    mocker: MockerFixture,
):
    provider = AsyncMock()
    provider.verify_id_token.side_effect = ValueError("invalid token")
    mocker.patch(_PROVIDER_PATH, return_value=provider)

    response = await http_client.post(ENDPOINT, json=make_apple_body())
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# Validation tests (422 Unprocessable Entity)
# ---------------------------------------------------------------------------


async def test_login_apple_missing_id_token_returns_422(
    http_client: AsyncClient,
    mock_apple_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json={})
    assert response.status_code == 422
