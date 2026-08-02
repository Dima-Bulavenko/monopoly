"""In-process WebSocket connection store for local development.

Production uses a persistent store (e.g. DynamoDB); locally, metadata is kept
in a plain dict — no external dependencies required.
"""

from __future__ import annotations

from app.application.websocket.interfaces import IWebSocketConnectionStore


class LocalConnectionStore(IWebSocketConnectionStore):
    """In-memory store for per-connection metadata."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, str]] = {}
        self._user_to_connection: dict[str, str] = {}

    async def save(
        self, connection_id: str, user_id: str, params: dict[str, str]
    ) -> None:
        self._data[connection_id] = {"user_id": user_id, **params}
        self._user_to_connection[user_id] = connection_id

    async def load(self, connection_id: str) -> dict[str, str] | None:
        return self._data.get(connection_id)

    async def delete(self, connection_id: str) -> None:
        meta = self._data.pop(connection_id, None)
        if meta:
            self._user_to_connection.pop(meta["user_id"], None)

    async def connection_for_user(self, user_id: str) -> str | None:
        return self._user_to_connection.get(user_id)
