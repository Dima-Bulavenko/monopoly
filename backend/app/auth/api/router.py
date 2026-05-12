"""Auth HTTP router — 6 endpoints mounted at /auth."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.auth.api.deps import (
    AuthServiceDep,
    get_apple_provider,
    get_google_provider,
)
from app.auth.application.dto import (
    AccessTokenResponse,
    LoginRequest,
    OAuthLoginRequest,
    RegisterRequest,
)
from app.auth.domain.exceptions import (
    AuthError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.config import settings

_COOKIE_NAME = "refresh_token"
_COOKIE_PATH = "/auth"
_COOKIE_MAX_AGE = settings.refresh_token_expire_days * 86_400


class _ErrorResponse(BaseModel):
    detail: str


_AUTH_401: dict[int | str, dict[str, Any]] = {
    401: {"model": _ErrorResponse, "description": "Authentication failed"},
}

router = APIRouter(prefix="/auth", tags=["auth"])


def _device_hint(request: Request) -> str | None:
    return request.headers.get("User-Agent")


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="strict",
        secure=not settings.is_local,  # HTTPS only in production
        path=_COOKIE_PATH,
        max_age=_COOKIE_MAX_AGE,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=_COOKIE_NAME, path=_COOKIE_PATH)


@router.post(
    "/register",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": _ErrorResponse, "description": "Email already registered"}
    },
)
async def register(
    body: RegisterRequest,
    svc: AuthServiceDep,
    request: Request,
    response: Response,
) -> AccessTokenResponse:
    try:
        result = await svc.register(body, device_hint=_device_hint(request))
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    _set_refresh_cookie(response, result.refresh_token)
    return AccessTokenResponse(access_token=result.access_token)


@router.post("/login", response_model=AccessTokenResponse, responses=_AUTH_401)
async def login(
    body: LoginRequest,
    svc: AuthServiceDep,
    request: Request,
    response: Response,
) -> AccessTokenResponse:
    try:
        result = await svc.login(body, device_hint=_device_hint(request))
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    _set_refresh_cookie(response, result.refresh_token)
    return AccessTokenResponse(access_token=result.access_token)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    responses={
        401: {
            "model": _ErrorResponse,
            "description": "Refresh token expired or invalid",
        }
    },
)
async def refresh(
    svc: AuthServiceDep,
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=_COOKIE_NAME),
) -> AccessTokenResponse:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )
    try:
        result = await svc.refresh(refresh_token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    _set_refresh_cookie(response, result.refresh_token)
    return AccessTokenResponse(access_token=result.access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    svc: AuthServiceDep,
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=_COOKIE_NAME),
) -> None:
    if refresh_token is not None:
        await svc.logout(refresh_token)
    _clear_refresh_cookie(response)


@router.post("/google", response_model=AccessTokenResponse, responses=_AUTH_401)
async def login_google(
    body: OAuthLoginRequest,
    svc: AuthServiceDep,
    response: Response,
) -> AccessTokenResponse:
    try:
        provider = get_google_provider()
        result = await svc.login_with_oauth(body, provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    _set_refresh_cookie(response, result.refresh_token)
    return AccessTokenResponse(access_token=result.access_token)


@router.post("/apple", response_model=AccessTokenResponse, responses=_AUTH_401)
async def login_apple(
    body: OAuthLoginRequest,
    svc: AuthServiceDep,
    response: Response,
) -> AccessTokenResponse:
    try:
        provider = get_apple_provider()
        result = await svc.login_with_oauth(body, provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    _set_refresh_cookie(response, result.refresh_token)
    return AccessTokenResponse(access_token=result.access_token)
