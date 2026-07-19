"""FastAPI HTTP routes for game lobby management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep
from app.application.dto.game_dto import (
    CreateGameDTO,
    ReadGameDTO,
    GameStateResponse,
)
from app.application.game_service import GameService
from app.config import settings
from app.infrastructure.db.connection_repository import ConnectionRepository
from app.infrastructure.db.game_repository import GameNotFoundError, GameRepository
from app.infrastructure.websocket.broadcaster import WebSocketBroadcaster
from app.infrastructure.websocket.local_broadcaster import LocalWebSocketBroadcaster

router = APIRouter(prefix="/games", tags=["games"])


def _make_game_service() -> GameService:
    repo = GameRepository()
    if settings.is_local:
        broadcaster = LocalWebSocketBroadcaster()
    else:
        conn_repo = ConnectionRepository()
        broadcaster = WebSocketBroadcaster(conn_repo)
    return GameService(repo, broadcaster)



@router.post("/", response_model=ReadGameDTO, status_code=status.HTTP_201_CREATED)
async def create_game(
    body: CreateGameDTO, current_user: CurrentUserDep
) -> ReadGameDTO:
    
    return ReadGameDTO(game_id="gav")


@router.post("/{game_id}/join", response_model=ReadGameDTO)
async def join_game(game_id: str, current_user: CurrentUserDep) -> ReadGameDTO:
    svc = _make_game_service()
    try:
        game, _ = await svc.join_game(
            game_id,
            player_name=current_user.display_name,
            user_id=current_user.user_id,
        )
    except GameNotFoundError:
        raise HTTPException(status_code=404, detail="Game not found")
    return ReadGameDTO(
        game_id=game.game_id,
    )


@router.post("/{game_id}/start", status_code=status.HTTP_204_NO_CONTENT)
async def start_game(game_id: str, current_user: CurrentUserDep) -> None:
    svc = _make_game_service()
    try:
        await svc.start_game(game_id)
    except GameNotFoundError:
        raise HTTPException(status_code=404, detail="Game not found")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{game_id}/state", response_model=GameStateResponse)
async def get_game_state(
    game_id: str, current_user: CurrentUserDep
) -> GameStateResponse:
    svc = _make_game_service()
    try:
        game = await svc.get_game_state(game_id)
    except GameNotFoundError:
        raise HTTPException(status_code=404, detail="Game not found")

    return game
