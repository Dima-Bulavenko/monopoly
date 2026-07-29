"""In-process WebSocket connection store for local development.

Production uses a persistent store (e.g. DynamoDB); locally, metadata is kept
in a plain dict — no external dependencies required.
"""

from __future__ import annotations

from app.application.websocket.interfaces import WebSocketConnectionStore


class LocalConnectionStore(WebSocketConnectionStore):
    """In-memory store for per-connection metadata."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, str]] = {}

    async def save(
        self, connection_id: str, user_id: str, params: dict[str, str]
    ) -> None:
        self._data[connection_id] = {"user_id": user_id, **params}

    async def load(self, connection_id: str) -> dict[str, str] | None:
        return self._data.get(connection_id)

    async def delete(self, connection_id: str) -> None:
        self._data.pop(connection_id, None)
