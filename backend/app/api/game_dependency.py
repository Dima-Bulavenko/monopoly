from __future__ import annotations
from fastapi import Depends
from typing import Annotated
from app.application.game_service import (
    CreateGameUseCase,
    JoinGameUseCase,
    GetGameUseCase,
    StartGameUseCase,
)
from app.infrastructure.db.game_repository import GameRepository
from app.application.event_bus import IEventBus
from app.bootstrap import container


def get_game_repository() -> GameRepository:
    return GameRepository()


def get_event_bus() -> IEventBus:
    return container.event_bus


GameRepositoryDep = Annotated[GameRepository, Depends(get_game_repository)]

EventBusDep = Annotated[IEventBus, Depends(get_event_bus)]


def create_game_use_case(game_repo: GameRepositoryDep) -> CreateGameUseCase:
    return CreateGameUseCase(game_repo)


def join_game_use_case(
    game_repo: GameRepositoryDep,
    event_bus: EventBusDep,
    start_game_use_case: StartGameUseCaseDep,
) -> JoinGameUseCase:
    return JoinGameUseCase(game_repo, event_bus, start_game_use_case)


def get_game_use_case(game_repo: GameRepositoryDep) -> GetGameUseCase:
    return GetGameUseCase(game_repo)


def start_game_use_case(
    game_repo: GameRepositoryDep, event_bus: EventBusDep
) -> StartGameUseCase:
    return StartGameUseCase(game_repo, event_bus)


CreateGameUseCaseDep = Annotated[CreateGameUseCase, Depends(create_game_use_case)]
JoinGameUseCaseDep = Annotated[JoinGameUseCase, Depends(join_game_use_case)]
GetGameUseCaseDep = Annotated[GetGameUseCase, Depends(get_game_use_case)]
StartGameUseCaseDep = Annotated[StartGameUseCase, Depends(start_game_use_case)]
