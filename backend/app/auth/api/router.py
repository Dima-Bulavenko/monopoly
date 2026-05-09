"""Auth HTTP router — 6 endpoints mounted at /auth."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.auth.api.deps import (
    AuthServiceDep,
    get_apple_provider,
    get_google_provider,
)
from app.auth.application.dto import (
    LoginRequest,
    LogoutRequest,
    OAuthLoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.domain.exceptions import (
    AuthError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
)


class _ErrorResponse(BaseModel):
    detail: str


_AUTH_401: dict[int | str, dict[str, Any]] = {
    401: {"model": _ErrorResponse, "description": "Authentication failed"},
}

router = APIRouter(prefix="/auth", tags=["auth"])


def _device_hint(request: Request) -> str | None:
    return request.headers.get("User-Agent")


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": _ErrorResponse, "description": "Email already registered"}
    },
)
async def register(
    body: RegisterRequest,
    svc: AuthServiceDep,
    request: Request,
) -> TokenResponse:
    try:
        return await svc.register(body, device_hint=_device_hint(request))
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/login", response_model=TokenResponse, responses=_AUTH_401)
async def login(
    body: LoginRequest,
    svc: AuthServiceDep,
    request: Request,
) -> TokenResponse:
    try:
        return await svc.login(body, device_hint=_device_hint(request))
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        401: {
            "model": _ErrorResponse,
            "description": "Refresh token expired or invalid",
        }
    },
)
async def refresh(body: RefreshRequest, svc: AuthServiceDep) -> TokenResponse:
    try:
        return await svc.refresh(body)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: LogoutRequest, svc: AuthServiceDep) -> None:
    await svc.logout(body)


@router.post("/google", response_model=TokenResponse, responses=_AUTH_401)
async def login_google(
    body: OAuthLoginRequest,
    svc: AuthServiceDep,
) -> TokenResponse:
    try:
        provider = get_google_provider()
        return await svc.login_with_oauth(body, provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post("/apple", response_model=TokenResponse, responses=_AUTH_401)
async def login_apple(
    body: OAuthLoginRequest,
    svc: AuthServiceDep,
) -> TokenResponse:
    try:
        provider = get_apple_provider()
        return await svc.login_with_oauth(body, provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
