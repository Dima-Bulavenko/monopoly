"""Auth application service.

Depends only on domain Protocols — no infrastructure imports.
Transaction boundary is owned by the session (via get_session in the API layer).
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.auth.application.dto import (
    LoginRequest,
    OAuthLoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.domain.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.auth.domain.oauth import OAuthProvider
from app.auth.domain.repository import TokenRepository, UserRepository
from app.auth.domain.token_service import JWTSigner, JWTVerifier, PasswordHasher


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: TokenRepository,
        jwt_signer: JWTSigner,
        jwt_verifier: JWTVerifier,
        password_hasher: PasswordHasher,
        refresh_token_expire_days: int,
    ) -> None:
        self._user_repo = user_repo
        self._token_repo = token_repo
        self._signer = jwt_signer
        self._verifier = jwt_verifier
        self._hasher = password_hasher
        self._refresh_expire_days = refresh_token_expire_days

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def register(
        self, req: RegisterRequest, device_hint: str | None = None
    ) -> TokenResponse:
        existing = await self._user_repo.get_by_email(req.email)
        if existing is not None:
            raise EmailAlreadyRegisteredError(req.email)

        hashed = self._hasher.hash(req.password)
        user = await self._user_repo.create(
            email=req.email,
            hashed_password=hashed,
            display_name=req.display_name,
        )
        return await self._issue_tokens(user.id, user.display_name, device_hint)

    async def login(
        self, req: LoginRequest, device_hint: str | None = None
    ) -> TokenResponse:
        user = await self._user_repo.get_by_email(req.email)
        if user is None or user.hashed_password is None:
            raise InvalidCredentialsError
        if not self._hasher.verify(req.password, user.hashed_password):
            raise InvalidCredentialsError
        return await self._issue_tokens(user.id, user.display_name, device_hint)

    async def login_with_oauth(
        self,
        req: OAuthLoginRequest,
        provider: OAuthProvider,
    ) -> TokenResponse:
        identity = await provider.verify_id_token(req.id_token)

        oauth_account = await self._user_repo.get_oauth_account(
            identity.provider, identity.provider_user_id
        )

        if oauth_account is not None:
            user = await self._user_repo.get_by_id(oauth_account.user_id)
            if user is None:
                raise InvalidTokenError
        else:
            # Find existing user by email or create a new one
            user = await self._user_repo.get_by_email(identity.email)
            if user is None:
                user = await self._user_repo.create(
                    email=identity.email,
                    hashed_password=None,
                    display_name=identity.display_name,
                )
            await self._user_repo.upsert_oauth_account(
                user_id=user.id,
                provider=identity.provider,
                provider_user_id=identity.provider_user_id,
            )

        return await self._issue_tokens(user.id, user.display_name, req.device_hint)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        token_hash = _hash_token(refresh_token)
        stored = await self._token_repo.get_refresh_token(token_hash)
        if stored is None or not stored.is_valid:
            raise InvalidTokenError

        user = await self._user_repo.get_by_id(stored.user_id)
        if user is None:
            raise InvalidTokenError

        # Rotate: revoke old, issue new
        await self._token_repo.revoke_refresh_token(token_hash)
        return await self._issue_tokens(
            stored.user_id, user.display_name, stored.device_hint
        )

    async def logout(self, refresh_token: str) -> None:
        token_hash = _hash_token(refresh_token)
        await self._token_repo.revoke_refresh_token(token_hash)

    async def logout_all(self, user_id: UUID) -> None:
        await self._token_repo.revoke_all_for_user(user_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _issue_tokens(
        self, user_id: UUID, display_name: str, device_hint: str | None
    ) -> TokenResponse:
        access_token = self._signer.sign(
            {"sub": str(user_id), "display_name": display_name}
        )

        raw_refresh = secrets.token_urlsafe(32)
        token_hash = _hash_token(raw_refresh)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self._refresh_expire_days
        )
        await self._token_repo.create_refresh_token(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
            device_hint=device_hint,
        )

        return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()
