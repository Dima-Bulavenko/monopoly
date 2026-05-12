"""Tests for POST /auth/register."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

ENDPOINT = "/auth/register"


# ---------------------------------------------------------------------------
# Module-level HTTP client — configured specifically for the register endpoint
# ---------------------------------------------------------------------------


@pytest.fixture
async def http_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient pointed at the test app.

    Defined here (not in conftest) so each endpoint module can apply its own
    transport settings, default headers, or base-URL tweaks.
    """
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Request body factory
# ---------------------------------------------------------------------------


@pytest.fixture
def make_register_body() -> Any:
    """Return a factory that builds a valid register payload.

    Individual fields can be overridden via keyword arguments:

        make_register_body(email="other@example.com")
    """

    def factory(**overrides: Any) -> dict[str, Any]:
        return {
            "email": "alice@example.com",
            "password": "Str0ng!Pass",
            "display_name": "Alice",
            **overrides,
        }

    return factory


# ---------------------------------------------------------------------------
# Shared response fixture — avoids repeating the POST in every happy-path test
# ---------------------------------------------------------------------------


@pytest.fixture
async def register_response(http_client: AsyncClient, make_register_body: Any):
    """POST a single valid registration and return the response."""
    return await http_client.post(ENDPOINT, json=make_register_body())


# ---------------------------------------------------------------------------
# Happy-path tests (201 Created)
# ---------------------------------------------------------------------------


async def test_register_returns_201(register_response):
    assert register_response.status_code == 201


async def test_register_body_has_access_token(register_response):
    body = register_response.json()
    assert "access_token" in body
    assert body["access_token"]


async def test_register_token_type_is_bearer(register_response):
    assert register_response.json()["token_type"] == "bearer"


async def test_register_sets_refresh_token_cookie(register_response):
    assert "refresh_token" in register_response.cookies


async def test_register_refresh_cookie_is_httponly(register_response):
    set_cookie = register_response.headers.get("set-cookie", "")
    assert "httponly" in set_cookie.lower()


async def test_register_refresh_cookie_path_is_auth(register_response):
    set_cookie = register_response.headers.get("set-cookie", "")
    assert "path=/auth" in set_cookie.lower()


# ---------------------------------------------------------------------------
# Conflict tests (409 Conflict)
# ---------------------------------------------------------------------------


async def test_register_duplicate_email_returns_409(
    http_client: AsyncClient,
    make_register_body: Any,
):
    body = make_register_body()
    await http_client.post(ENDPOINT, json=body)
    response = await http_client.post(ENDPOINT, json=body)
    assert response.status_code == 409


async def test_register_duplicate_email_response_has_detail(
    http_client: AsyncClient,
    make_register_body: Any,
):
    body = make_register_body()
    await http_client.post(ENDPOINT, json=body)
    response = await http_client.post(ENDPOINT, json=body)
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# Validation tests (422 Unprocessable Entity)
# ---------------------------------------------------------------------------


async def test_register_invalid_email_returns_422(
    http_client: AsyncClient,
    make_register_body: Any,
):
    response = await http_client.post(
        ENDPOINT,
        json=make_register_body(email="not-an-email"),
    )
    assert response.status_code == 422


async def test_register_missing_email_returns_422(
    http_client: AsyncClient,
    make_register_body: Any,
):
    body = make_register_body()
    del body["email"]
    response = await http_client.post(ENDPOINT, json=body)
    assert response.status_code == 422


async def test_register_missing_password_returns_422(
    http_client: AsyncClient,
    make_register_body: Any,
):
    body = make_register_body()
    del body["password"]
    response = await http_client.post(ENDPOINT, json=body)
    assert response.status_code == 422


async def test_register_missing_display_name_returns_422(
    http_client: AsyncClient,
    make_register_body: Any,
):
    body = make_register_body()
    del body["display_name"]
    response = await http_client.post(ENDPOINT, json=body)
    assert response.status_code == 422
