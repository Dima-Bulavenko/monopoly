"""FastAPI HTTP routes for game lobby management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep
from app.application.dto.game_dto import (
    CreateGameDTO,
    ReadGameDTO,
)
from app.api.game_dependency import CreateGameUseCaseDep
from app.api.http.schemas import ErrorResponseModel
from app.domain.game.exceptions import GameAlreadyExistsError

router = APIRouter(prefix="/games", tags=["games"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Game already exists",
            "model": ErrorResponseModel,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": ErrorResponseModel,
        },
    },
)
async def create_game(
    body: CreateGameDTO,
    current_user: CurrentUserDep,
    create_game_use_case: CreateGameUseCaseDep,
) -> ReadGameDTO:
    try:
        game = await create_game_use_case.execute(
            current_user.user_id, current_user.display_name, body
        )
    except GameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Game already exists"
        )
    return ReadGameDTO.model_validate(game, from_attributes=True)
