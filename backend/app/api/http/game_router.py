"""FastAPI HTTP routes for game lobby management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep
from app.application.dto.game_dto import (
    CreateGameDTO,
    ReadGameDTO,
)
from app.api.game_dependency import (
    CreateGameUseCaseDep,
    JoinGameUseCaseDep,
    GetGameUseCaseDep,
    StartGameUseCaseDep,
)
from app.api.http.schemas import ErrorResponseModel
from app.domain.game.exceptions import (
    GameAlreadyExistsError,
    GameNotFoundError,
    GameAlreadyStartedError,
)

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
    return game


@router.patch(
    "/{game_id}/join",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Game not found",
            "model": ErrorResponseModel,
        },
    },
)
async def join_game(
    game_id: str,
    current_user: CurrentUserDep,
    join_game_use_case: JoinGameUseCaseDep,
) -> ReadGameDTO:
    try:
        game = await join_game_use_case.execute(
            current_user.user_id, current_user.display_name, game_id
        )
    except GameNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    return game


@router.get(
    "/{game_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Game not found",
            "model": ErrorResponseModel,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": ErrorResponseModel,
        },
    },
)
async def get_game(
    game_id: str, _: CurrentUserDep, get_game_use_case: GetGameUseCaseDep
) -> ReadGameDTO:
    try:
        game = await get_game_use_case.execute(game_id)
    except GameNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    return game


@router.patch(
    "/{game_id}/start",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Game not found",
            "model": ErrorResponseModel,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": ErrorResponseModel,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Game already started",
            "model": ErrorResponseModel,
        },
    },
    include_in_schema=False,
)
async def start_game(
    game_id: str, _: CurrentUserDep, start_game_use_case: StartGameUseCaseDep
) -> None:
    try:
        await start_game_use_case.execute(game_id)
    except GameNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    except GameAlreadyStartedError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Game already started"
        )
