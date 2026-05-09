"""argon2 implementation of PasswordHasher via pwdlib."""

from __future__ import annotations

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class Argon2PasswordHasher:
    def __init__(self) -> None:
        self._ph = PasswordHash((Argon2Hasher(),))

    def hash(self, plain: str) -> str:
        return self._ph.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            return self._ph.verify(plain, hashed)
        except Exception:
            return False
