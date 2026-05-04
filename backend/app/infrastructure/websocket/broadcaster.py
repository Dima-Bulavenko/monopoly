"""WebSocket broadcaster using API Gateway Management API."""

from __future__ import annotations

import dataclasses
import json
import os
from typing import TYPE_CHECKING, Protocol

import aioboto3

from app.domain.game.events import Event
from app.domain.game.models import Game

if TYPE_CHECKING:
    from app.infrastructure.db.connection_repository import ConnectionRepository


APIGW_ENDPOINT = os.environ.get("APIGW_MANAGEMENT_ENDPOINT")


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

        payload = json.dumps(
            {
                "type": "game_update",
                "events": [self._serialise_event(e) for e in events],
                "state": self._serialise_game(game),
            }
        ).encode()

        session = aioboto3.Session()
        async with session.client(
            "apigatewaymanagementapi",
            endpoint_url=APIGW_ENDPOINT,
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        ) as apigw:
            for conn in connections:
                conn_id = conn["connection_id"]
                try:
                    await apigw.post_to_connection(ConnectionId=conn_id, Data=payload)
                except apigw.exceptions.GoneException:
                    # Stale connection — clean up
                    await self._connection_repo.delete_connection(conn_id)

    @staticmethod
    def _serialise_event(event: Event) -> dict:
        d = dataclasses.asdict(event)
        d["type"] = type(event).__name__
        return d

    @staticmethod
    def _serialise_game(game: Game) -> dict:
        return dataclasses.asdict(game)
