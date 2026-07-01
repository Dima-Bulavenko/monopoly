"""Port: generic WebSocket connection metadata store.

Independent of any business domain — stores only the raw connection ID,
authenticated player ID, and the query-string params that arrived on connect.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class ConnectionMeta(TypedDict):
    user_id: str
    params: dict[str, str]


class AbstractConnectionStore(ABC):
    @abstractmethod
    async def save(
        self,
        connection_id: str,
        user_id: str,
        params: dict[str, str],
    ) -> None:
        """Persist metadata for a newly established connection."""

    @abstractmethod
    async def load(self, connection_id: str) -> ConnectionMeta | None:
        """Return metadata for *connection_id*, or ``None`` if unknown."""

    @abstractmethod
    async def delete(self, connection_id: str) -> None:
        """Remove the record for a closed or stale connection."""
