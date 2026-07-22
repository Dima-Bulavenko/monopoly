from __future__ import annotations

from app.domain.game.models import Game, Player
from app.application.dto.game_dto import ReadGameDTO, CreateGameDTO
from app.domain.game.exceptions import GameNotFoundError
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


class JoinGameUseCase:
    def __init__(self, game_repo: AbstractGameRepository) -> None:
        self._game_repo = game_repo

    async def execute(
        self, player_id: str, player_name: str, game_id: str
    ) -> ReadGameDTO:
        game = await self._game_repo.get(game_id)
        if not game:
            raise GameNotFoundError(f"Game with ID {game_id} not found")
        if any(player.player_id == player_id for player in game.players):
            return ReadGameDTO.model_validate(game, from_attributes=True)
        new_player = Player(player_id=player_id, name=player_name)
        game.players.append(new_player)
        await self._game_repo.update(game)

        return ReadGameDTO.model_validate(game, from_attributes=True)
