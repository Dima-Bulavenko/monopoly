"""Game-layer dependency injection.

This is the decoupling boundary between auth and game services.
Only JWTVerifier (public key) is imported here — no AuthService.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.auth.infrastructure.jwt.rs256_service import make_verifier

_bearer = HTTPBearer()


class CurrentUser(BaseModel, frozen=True):
    user_id: str
    display_name: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CurrentUser:
    try:
        payload = make_verifier().verify(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return CurrentUser(
        user_id=payload["sub"],
        display_name=payload.get("display_name", ""),
    )


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
