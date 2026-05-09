"""Dependency injection wiring for the auth API layer.

This is the only place that touches concrete infrastructure classes.
Everything above (AuthService, router) depends only on Protocols.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.application.auth_service import AuthService
from app.auth.infrastructure.db.postgres import get_session
from app.auth.infrastructure.db.token_repo import SQLTokenRepository
from app.auth.infrastructure.db.user_repo import SQLUserRepository
from app.auth.infrastructure.jwt.rs256_service import make_signer, make_verifier
from app.auth.infrastructure.oauth.apple import AppleOAuthProvider
from app.auth.infrastructure.oauth.google import GoogleOAuthProvider
from app.auth.infrastructure.password.argon2 import Argon2PasswordHasher
from app.config import settings

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(
        user_repo=SQLUserRepository(session),
        token_repo=SQLTokenRepository(session),
        jwt_signer=make_signer(),
        jwt_verifier=make_verifier(),
        password_hasher=Argon2PasswordHasher(),
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


def get_google_provider() -> GoogleOAuthProvider:
    if not settings.google_client_id:
        raise ValueError("GOOGLE_CLIENT_ID is not configured")
    return GoogleOAuthProvider(settings.google_client_id)


def get_apple_provider() -> AppleOAuthProvider:
    if not settings.apple_client_id:
        raise ValueError("APPLE_CLIENT_ID is not configured")
    return AppleOAuthProvider(settings.apple_client_id)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
