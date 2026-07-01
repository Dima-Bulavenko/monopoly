"""In-process connection metadata store for local development."""

from __future__ import annotations

from app.application.ports.connection_store import (
    AbstractConnectionStore,
    ConnectionMeta,
)


class InMemoryConnectionStore(AbstractConnectionStore):
    """Stores connection metadata in a plain dict — no external I/O."""

    def __init__(self) -> None:
        self._store: dict[str, ConnectionMeta] = {}

    async def save(
        self,
        connection_id: str,
        user_id: str,
        params: dict[str, str],
    ) -> None:
        self._store[connection_id] = ConnectionMeta(user_id=user_id, params=params)

    async def load(self, connection_id: str) -> ConnectionMeta | None:
        return self._store.get(connection_id)

    async def delete(self, connection_id: str) -> None:
        self._store.pop(connection_id, None)
