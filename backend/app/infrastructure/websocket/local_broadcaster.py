"""In-process WebSocket connection manager and broadcaster for local development.

In production, API Gateway manages connections.  Locally, FastAPI WebSocket
endpoints register themselves here, and the LocalWebSocketBroadcaster pushes
events directly to the connected sockets — no AWS required.
"""

from __future__ import annotations

import json
from collections import defaultdict

from fastapi import WebSocket

from app.application.dto.websocket_dto import (
    GameUpdateMessage,
    event_to_dto,
    game_to_dto,
)
from app.domain.game.events import Event
from app.domain.game.models import Game


class LocalConnectionManager:
    """Thread-safe (asyncio) registry of active WebSocket connections."""

    def __init__(self) -> None:
        # game_id → list of (player_id, WebSocket)
        self._connections: dict[str, list[tuple[str, WebSocket]]] = defaultdict(list)

    async def connect(self, game_id: str, player_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[game_id].append((player_id, ws))

    def disconnect(self, game_id: str, ws: WebSocket) -> None:
        self._connections[game_id] = [
            (pid, w) for pid, w in self._connections[game_id] if w is not ws
        ]

    async def broadcast(self, game_id: str, payload: dict) -> None:
        stale: list[WebSocket] = []
        for player_id, ws in list(self._connections[game_id]):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(game_id, ws)


# Singleton used by both the router and the broadcaster
local_manager = LocalConnectionManager()


class LocalWebSocketBroadcaster:
    """Broadcaster that pushes directly to LocalConnectionManager sockets."""

    async def broadcast(self, game_id: str, events: list[Event], game: Game) -> None:
        message = GameUpdateMessage(
            type="game_update",
            events=[event_to_dto(e) for e in events],
            state=game_to_dto(game),
        )
        await local_manager.broadcast(game_id, message.model_dump())
