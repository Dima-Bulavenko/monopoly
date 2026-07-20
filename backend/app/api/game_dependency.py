from fastapi import Depends
from typing import Annotated
from app.application.game_service import CreateGameUseCase
from app.infrastructure.db.game_repository import GameRepository


def create_game_use_case() -> CreateGameUseCase:
    return CreateGameUseCase(GameRepository())


CreateGameUseCaseDep = Annotated[CreateGameUseCase, Depends(create_game_use_case)]
