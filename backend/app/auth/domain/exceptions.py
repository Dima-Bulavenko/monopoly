"""Domain exceptions for the auth sub-package."""

from __future__ import annotations


class AuthError(Exception):
    """Base class for all auth domain errors."""


class EmailAlreadyRegisteredError(AuthError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: {email}")


class InvalidCredentialsError(AuthError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InvalidTokenError(AuthError):
    def __init__(self) -> None:
        super().__init__("Token is invalid or has expired")
