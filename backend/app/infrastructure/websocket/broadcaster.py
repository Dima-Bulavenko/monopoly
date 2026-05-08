"""WebSocket broadcaster using API Gateway Management API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import aioboto3

from app.application.dto.websocket_dto import (
    GameUpdateMessage,
    event_to_dto,
    game_to_dto,
)
from app.config import settings
from app.domain.game.events import Event
from app.domain.game.models import Game

if TYPE_CHECKING:
    from app.infrastructure.db.connection_repository import ConnectionRepository


class BroadcasterProtocol(Protocol):
    async def broadcast(
        self, game_id: str, events: list[Event], game: Game
    ) -> None: ...


class WebSocketBroadcaster:
    def __init__(self, connection_repo: "ConnectionRepository") -> None:
        self._connection_repo = connection_repo

    async def broadcast(self, game_id: str, events: list[Event], game: Game) -> None:
        connections = await self._connection_repo.list_connections_for_game(game_id)
        if not connections:
            return

        message = GameUpdateMessage(
            type="game_update",
            events=[event_to_dto(e) for e in events],
            state=game_to_dto(game),
        )
        payload = message.model_dump_json().encode()

        session = aioboto3.Session()
        async with session.client(
            "apigatewaymanagementapi",
            endpoint_url=settings.apigw_management_endpoint,
            region_name=settings.aws_region,
        ) as apigw:
            for conn in connections:
                conn_id = conn["connection_id"]
                try:
                    await apigw.post_to_connection(ConnectionId=conn_id, Data=payload)
                except apigw.exceptions.GoneException:
                    # Stale connection — clean up
                    await self._connection_repo.delete_connection(conn_id)
