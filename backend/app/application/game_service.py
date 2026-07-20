"""Application service orchestrating the game engine with persistence and broadcasting."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.game.models import Game, Player
from app.application.dto.game_dto import ReadGameDTO, CreateGameDTO

if TYPE_CHECKING:
    from app.application.ports.game_repository import AbstractGameRepository


class CreateGameUseCase:
    def __init__(self, game_repo: "AbstractGameRepository") -> None:
        self._game_repo = game_repo

    async def execute(
        self, player_id: str, player_name: str, game_data: CreateGameDTO
    ) -> ReadGameDTO:
        game = Game.model_validate(
            {**game_data.model_dump(), "host_player_id": player_id},
            from_attributes=True,
        )
        host = Player(player_id=player_id, name=player_name)
        game.players.append(host)
        await self._game_repo.create(game)
        return ReadGameDTO.model_validate(game, from_attributes=True)
