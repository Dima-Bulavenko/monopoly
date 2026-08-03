from app.application.websocket.interfaces import (
    IWebSocketBroadcaster,
    IWebSocketConnectionStore,
)
from app.application.websocket.messages import JoinedGameMessage
from app.domain.game.repository import IGameRepository


class JoinedGameHandler:
    def __init__(
        self,
        broadcaster: IWebSocketBroadcaster,
        store: IWebSocketConnectionStore,
        game_repo: IGameRepository,
    ) -> None:
        self._broadcaster = broadcaster
        self._store = store
        self._game_repo = game_repo

    async def handle(self, message: JoinedGameMessage) -> None:
        game = await self._game_repo.get(message.payload.game_id)
        if game is None:
            return

        other_player_ids = [
            p.player_id
            for p in game.players
            if p.player_id != message.payload.player.player_id
        ]

        connection_ids = []
        for player_id in other_player_ids:
            conn_id = await self._store.connection_for_user(str(player_id))
            if conn_id is not None:
                connection_ids.append(conn_id)
        if connection_ids:
            await self._broadcaster.broadcast(connection_ids, message.model_dump_json())
