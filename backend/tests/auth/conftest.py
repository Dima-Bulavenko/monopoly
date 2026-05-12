"""Auth-specific fixtures shared across all auth endpoint tests."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient


_DEFAULT_USER_EMAIL = "testuser@example.com"
_DEFAULT_USER_PASSWORD = "Str0ng!Pass"
_DEFAULT_USER_DISPLAY_NAME = "Test User"


@pytest.fixture
async def registered_user(http_client: AsyncClient) -> dict[str, Any]:
    """Register a user via the API and return credentials + tokens.

    Each test module provides its own ``http_client``, so this fixture
    transparently uses the per-module transport configuration.

    Returns a dict with keys: email, password, display_name, access_token,
    refresh_token.
    """
    body = {
        "email": _DEFAULT_USER_EMAIL,
        "password": _DEFAULT_USER_PASSWORD,
        "display_name": _DEFAULT_USER_DISPLAY_NAME,
    }
    response = await http_client.post("/auth/register", json=body)
    assert response.status_code == 201, response.text
    return {
        "email": body["email"],
        "password": body["password"],
        "display_name": body["display_name"],
        "access_token": response.json()["access_token"],
        "refresh_token": response.cookies["refresh_token"],
    }
