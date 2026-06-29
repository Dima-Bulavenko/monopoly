"""FastAPI WebSocket router for local development.

Replaces API Gateway WebSocket in dev.  The frontend connects to:
  ws://localhost:8001/ws/{game_id}?token={access_token}

Messages from client:  {"action": "roll_dice", "payload": {}}
Messages to client:    {"type": "game_update", "events": [...], "state": {...}}
"""

from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.websocket.handlers import _build_command
from app.application.dto.websocket_dto import (
    GameUpdateMessage,
    GetLobbyStateMessage,
    InboundAdapter,
    game_to_dto,
)
from app.application.game_service import GameService
from app.auth.infrastructure.jwt.rs256_service import make_verifier
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
async def websocket_endpoint(ws: WebSocket, game_id: str, token: str) -> None:
    try:
        payload = make_verifier().verify(token)
    except ValueError:
        await ws.close(code=1008)  # Policy Violation — invalid/expired token
        return
    player_id: str = payload["sub"]
    await local_manager.connect(game_id, player_id, ws)

    # Push current game state immediately so the client can render the lobby
    # without waiting for another player to join.
    svc = _make_game_service()
    try:
        game = await svc.get_game_state(game_id)
        init_msg = GameUpdateMessage(
            type="game_update", events=[], state=game_to_dto(game)
        )
        await ws.send_text(init_msg.model_dump_json())
    except GameNotFoundError:
        await ws.close(code=4004)
        return

    try:
        while True:
            raw = await ws.receive_text()
            try:
                body = json.loads(raw)
                msg = InboundAdapter.validate_python(body)
            except (KeyError, ValueError) as exc:
                await ws.send_text(json.dumps({"type": "error", "message": str(exc)}))
                continue

            if isinstance(msg, GetLobbyStateMessage):
                svc = _make_game_service()
                try:
                    game = await svc.get_game_state(game_id)
                    resp = GameUpdateMessage(
                        type="game_update", events=[], state=game_to_dto(game)
                    )
                    await ws.send_text(resp.model_dump_json())
                except GameNotFoundError:
                    await ws.send_text(
                        json.dumps({"type": "error", "message": "Game not found"})
                    )
                continue

            try:
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
