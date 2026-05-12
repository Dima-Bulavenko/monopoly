"""Pydantic DTOs for the auth application layer."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OAuthLoginRequest(BaseModel):
    id_token: str
    device_hint: str | None = None


class TokenResponse(BaseModel):
    """Internal DTO — carries both tokens within the service layer."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    """Public API response — only the short-lived access token.

    The refresh token is delivered via an httpOnly cookie by the router.
    """

    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Kept for backwards-compat; refresh_token is now read from cookie in the router."""


class LogoutRequest(BaseModel):
    """Kept for backwards-compat; refresh_token is now read from cookie in the router."""
