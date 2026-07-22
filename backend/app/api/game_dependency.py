from fastapi import Depends
from typing import Annotated
from app.application.game_service import CreateGameUseCase, JoinGameUseCase
from app.infrastructure.db.game_repository import GameRepository


def get_game_repository() -> GameRepository:
    return GameRepository()


GameRepositoryDep = Annotated[GameRepository, Depends(get_game_repository)]


def create_game_use_case(game_repo: GameRepositoryDep) -> CreateGameUseCase:
    return CreateGameUseCase(game_repo)


def join_game_use_case(game_repo) -> JoinGameUseCase:
    return JoinGameUseCase(game_repo)


CreateGameUseCaseDep = Annotated[CreateGameUseCase, Depends(create_game_use_case)]
JoinGameUseCaseDep = Annotated[JoinGameUseCase, Depends(join_game_use_case)]
