"""Application service for managing WebSocket connections."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application.ports.connection_repository import AbstractConnectionRepository


class ConnectionService:
    def __init__(self, connection_repo: "AbstractConnectionRepository") -> None:
        self._repo = connection_repo

    async def on_connect(
        self, connection_id: str, game_id: str, player_id: str
    ) -> None:
        await self._repo.save_connection(connection_id, game_id, player_id)

    async def on_disconnect(self, connection_id: str) -> None:
        await self._repo.delete_connection(connection_id)

    async def get_game_connections(self, game_id: str) -> list[dict]:
        return await self._repo.list_connections_for_game(game_id)
