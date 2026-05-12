"""Tests for POST /auth/login."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

ENDPOINT = "/auth/login"


@pytest.fixture
async def http_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def make_login_body() -> Any:
    """Return a factory that builds a valid login payload."""

    def factory(**overrides: Any) -> dict[str, Any]:
        return {
            "email": "testuser@example.com",
            "password": "Str0ng!Pass",
            **overrides,
        }

    return factory


# ---------------------------------------------------------------------------
# Happy-path tests (200 OK)
# ---------------------------------------------------------------------------


async def test_login_returns_200(
    http_client: AsyncClient,
    make_login_body: Any,
    registered_user: dict,
):
    response = await http_client.post(ENDPOINT, json=make_login_body())
    assert response.status_code == 200


async def test_login_body_has_access_token(
    http_client: AsyncClient,
    make_login_body: Any,
    registered_user: dict,
):
    response = await http_client.post(ENDPOINT, json=make_login_body())
    body = response.json()
    assert "access_token" in body
    assert body["access_token"]


async def test_login_token_type_is_bearer(
    http_client: AsyncClient,
    make_login_body: Any,
    registered_user: dict,
):
    response = await http_client.post(ENDPOINT, json=make_login_body())
    assert response.json()["token_type"] == "bearer"


async def test_login_sets_refresh_token_cookie(
    http_client: AsyncClient,
    make_login_body: Any,
    registered_user: dict,
):
    response = await http_client.post(ENDPOINT, json=make_login_body())
    assert "refresh_token" in response.cookies


async def test_login_refresh_cookie_is_httponly(
    http_client: AsyncClient,
    make_login_body: Any,
    registered_user: dict,
):
    response = await http_client.post(ENDPOINT, json=make_login_body())
    set_cookie = response.headers.get("set-cookie", "")
    assert "httponly" in set_cookie.lower()


async def test_login_refresh_cookie_path_is_auth(
    http_client: AsyncClient,
    make_login_body: Any,
    registered_user: dict,
):
    response = await http_client.post(ENDPOINT, json=make_login_body())
    set_cookie = response.headers.get("set-cookie", "")
    assert "path=/auth" in set_cookie.lower()


# ---------------------------------------------------------------------------
# Invalid credentials tests (401 Unauthorized)
# ---------------------------------------------------------------------------


async def test_login_wrong_password_returns_401(
    http_client: AsyncClient,
    make_login_body: Any,
    registered_user: dict,
):
    response = await http_client.post(
        ENDPOINT,
        json=make_login_body(password="wrong-password"),
    )
    assert response.status_code == 401


async def test_login_unknown_email_returns_401(
    http_client: AsyncClient,
    make_login_body: Any,
):
    response = await http_client.post(
        ENDPOINT,
        json=make_login_body(email="nobody@example.com"),
    )
    assert response.status_code == 401


async def test_login_invalid_credentials_response_has_detail(
    http_client: AsyncClient,
    make_login_body: Any,
    registered_user: dict,
):
    response = await http_client.post(
        ENDPOINT,
        json=make_login_body(password="wrong-password"),
    )
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# Validation tests (422 Unprocessable Entity)
# ---------------------------------------------------------------------------


async def test_login_missing_email_returns_422(
    http_client: AsyncClient,
    make_login_body: Any,
):
    body = make_login_body()
    del body["email"]
    response = await http_client.post(ENDPOINT, json=body)
    assert response.status_code == 422


async def test_login_missing_password_returns_422(
    http_client: AsyncClient,
    make_login_body: Any,
):
    body = make_login_body()
    del body["password"]
    response = await http_client.post(ENDPOINT, json=body)
    assert response.status_code == 422


async def test_login_invalid_email_format_returns_422(
    http_client: AsyncClient,
    make_login_body: Any,
):
    response = await http_client.post(
        ENDPOINT,
        json=make_login_body(email="not-an-email"),
    )
    assert response.status_code == 422
