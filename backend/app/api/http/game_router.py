"""FastAPI HTTP routes for game lobby management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep
from app.application.dto.game_dto import (
    CreateGameRequest,
    GameResponse,
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


@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    body: CreateGameRequest, current_user: CurrentUserDep
) -> GameResponse:
    svc = _make_game_service()
    game = await svc.create_game(
        host_name=current_user.display_name,
        user_id=current_user.user_id,
        max_players=body.max_players,
    )
    return GameResponse(
        game_id=game.game_id,
        status=game.status.value,
        player_count=len(game.players),
        max_players=game.max_players,
    )


@router.post("/{game_id}/join", response_model=GameResponse)
async def join_game(game_id: str, current_user: CurrentUserDep) -> GameResponse:
    svc = _make_game_service()
    try:
        game, _ = await svc.join_game(
            game_id,
            player_name=current_user.display_name,
            user_id=current_user.user_id,
        )
    except GameNotFoundError:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameResponse(
        game_id=game.game_id,
        status=game.status.value,
        player_count=len(game.players),
        max_players=game.max_players,
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

    return GameStateResponse(
        game_id=game.game_id,
        status=game.status.value,
        phase=game.phase.value,
        current_player_id=(game.current_player.player_id if game.players else None),
        players=[
            {
                "player_id": p.player_id,
                "name": p.name,
                "position": p.position,
                "balance": p.balance,
                "in_jail": p.in_jail,
                "is_bankrupt": p.is_bankrupt,
            }
            for p in game.players
        ],
        properties={
            str(k): {
                "square_index": v.square_index,
                "owner_id": v.owner_id,
                "houses": v.houses,
                "hotel": v.hotel,
                "mortgaged": v.mortgaged,
            }
            for k, v in game.properties.items()
        },
        free_parking_pot=game.free_parking_pot,
        max_players=game.max_players,
    )
