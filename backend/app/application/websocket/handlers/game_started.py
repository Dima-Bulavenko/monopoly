from app.application.websocket.interfaces import (
    IWebSocketBroadcaster,
    IWebSocketConnectionStore,
)
from app.application.websocket.messages import GameStartedMessage
from app.domain.game.repository import IGameRepository
import asyncio


class GameStartedHandler:
    def __init__(
        self,
        broadcaster: IWebSocketBroadcaster,
        store: IWebSocketConnectionStore,
        game_repo: IGameRepository,
    ) -> None:
        self._broadcaster = broadcaster
        self._store = store
        self._game_repo = game_repo

    async def handle(self, message: GameStartedMessage) -> None:
        game = await self._game_repo.get(message.payload.game_id)

        if not game:
            return
        tasks = [
            self._store.connection_for_user(player.player_id) for player in game.players
        ]
        results = await asyncio.gather(*tasks)
        connection_ids = [cid for cid in results if cid is not None]
        if connection_ids:
            await self._broadcaster.broadcast(connection_ids, message.model_dump_json())
