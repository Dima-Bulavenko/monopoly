"""Tests for POST /auth/google."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture

from app.auth.domain.oauth import OAuthIdentity

ENDPOINT = "/auth/google"
_PROVIDER_PATH = "app.auth.api.router.get_google_provider"


@pytest.fixture
async def http_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def google_identity() -> OAuthIdentity:
    """A valid OAuthIdentity as returned by the Google provider."""
    return OAuthIdentity(
        provider="google",
        provider_user_id="google-uid-001",
        email="googleuser@example.com",
        display_name="Google User",
    )


@pytest.fixture
def mock_google_provider(
    mocker: MockerFixture, google_identity: OAuthIdentity
) -> AsyncMock:
    """Patch get_google_provider to return a mock that verifies any id_token."""
    provider = AsyncMock()
    provider.verify_id_token.return_value = google_identity
    mocker.patch(_PROVIDER_PATH, return_value=provider)
    return provider


@pytest.fixture
def make_google_body() -> Any:
    def factory(**overrides: Any) -> dict[str, Any]:
        return {"id_token": "valid-google-id-token", **overrides}

    return factory


# ---------------------------------------------------------------------------
# Happy-path tests (200 OK)
# ---------------------------------------------------------------------------


async def test_login_google_returns_200(
    http_client: AsyncClient,
    make_google_body: Any,
    mock_google_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json=make_google_body())
    assert response.status_code == 200


async def test_login_google_body_has_access_token(
    http_client: AsyncClient,
    make_google_body: Any,
    mock_google_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json=make_google_body())
    body = response.json()
    assert "access_token" in body
    assert body["access_token"]


async def test_login_google_token_type_is_bearer(
    http_client: AsyncClient,
    make_google_body: Any,
    mock_google_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json=make_google_body())
    assert response.json()["token_type"] == "bearer"


async def test_login_google_sets_refresh_token_cookie(
    http_client: AsyncClient,
    make_google_body: Any,
    mock_google_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json=make_google_body())
    assert "refresh_token" in response.cookies


async def test_login_google_same_identity_reuses_existing_user(
    http_client: AsyncClient,
    make_google_body: Any,
    mock_google_provider: AsyncMock,
):
    # Two logins with the same Google identity must both succeed
    first = await http_client.post(ENDPOINT, json=make_google_body())
    second = await http_client.post(ENDPOINT, json=make_google_body())
    assert first.status_code == 200
    assert second.status_code == 200


# ---------------------------------------------------------------------------
# Error tests (401 Unauthorized)
# ---------------------------------------------------------------------------


async def test_login_google_invalid_token_returns_401(
    http_client: AsyncClient,
    make_google_body: Any,
    mocker: MockerFixture,
):
    provider = AsyncMock()
    provider.verify_id_token.side_effect = ValueError("invalid token")
    mocker.patch(_PROVIDER_PATH, return_value=provider)

    response = await http_client.post(ENDPOINT, json=make_google_body())
    assert response.status_code == 401


async def test_login_google_invalid_token_response_has_detail(
    http_client: AsyncClient,
    make_google_body: Any,
    mocker: MockerFixture,
):
    provider = AsyncMock()
    provider.verify_id_token.side_effect = ValueError("invalid token")
    mocker.patch(_PROVIDER_PATH, return_value=provider)

    response = await http_client.post(ENDPOINT, json=make_google_body())
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# Validation tests (422 Unprocessable Entity)
# ---------------------------------------------------------------------------


async def test_login_google_missing_id_token_returns_422(
    http_client: AsyncClient,
    mock_google_provider: AsyncMock,
):
    response = await http_client.post(ENDPOINT, json={})
    assert response.status_code == 422
