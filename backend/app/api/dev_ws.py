"""FastAPI WebSocket router for local development.

Replaces API Gateway WebSocket in dev.  The frontend connects to:
  ws://localhost:8001/ws/{game_id}?player_id={player_id}

Messages from client:  {"action": "roll_dice", "payload": {}}
Messages to client:    {"type": "game_update", "events": [...], "state": {...}}
"""

from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.websocket.handlers import _build_command
from app.application.dto.websocket_dto import InboundAdapter
from app.application.game_service import GameService
from app.domain.exceptions import DomainError
from app.infrastructure.db.game_repository import GameNotFoundError, GameRepository
from app.infrastructure.websocket.local_broadcaster import (
    LocalWebSocketBroadcaster,
    local_manager,
)

router = APIRouter(tags=["dev-websocket"])


def _make_game_service() -> GameService:
    repo = GameRepository()
    broadcaster = LocalWebSocketBroadcaster()
    return GameService(repo, broadcaster)


@router.websocket("/ws/{game_id}")
async def websocket_endpoint(ws: WebSocket, game_id: str, player_id: str) -> None:
    await local_manager.connect(game_id, player_id, ws)
    try:
        while True:
            raw = await ws.receive_text()
            try:
                body = json.loads(raw)
                msg = InboundAdapter.validate_python(body)
                command = _build_command(msg, player_id)
            except (KeyError, ValueError) as exc:
                await ws.send_text(json.dumps({"type": "error", "message": str(exc)}))
                continue

            svc = _make_game_service()
            try:
                await svc.handle_action(game_id, command)
            except GameNotFoundError:
                await ws.send_text(
                    json.dumps({"type": "error", "message": "Game not found"})
                )
            except DomainError as exc:
                await ws.send_text(json.dumps({"type": "error", "message": str(exc)}))

    except WebSocketDisconnect:
        local_manager.disconnect(game_id, ws)
