from __future__ import annotations

from abc import ABC, abstractmethod


class AbstractConnectionRepository(ABC):
    @abstractmethod
    async def save_connection(
        self, connection_id: str, game_id: str, player_id: str
    ) -> None: ...

    @abstractmethod
    async def delete_connection(self, connection_id: str) -> None: ...

    @abstractmethod
    async def list_connections_for_game(self, game_id: str) -> list[dict]: ...
