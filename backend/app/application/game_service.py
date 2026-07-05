"""Application service orchestrating the game engine with persistence and broadcasting."""

from __future__ import annotations

import dataclasses
from random import Random
from typing import TYPE_CHECKING

from app.domain.game.commands import Command
from app.domain.game.engine import GameEngine
from app.domain.game.events import Event, PlayerJoinedLobbyEvent
from app.domain.game.models import Game, GameStatus, Player
from app.application.dto.game_dto import GameStateResponse

if TYPE_CHECKING:
    from app.application.ports.broadcaster import AbstractBroadcaster
    from app.application.ports.game_repository import AbstractGameRepository


class GameService:
    def __init__(
        self,
        game_repo: "AbstractGameRepository",
        broadcaster: "AbstractBroadcaster",
        engine: GameEngine | None = None,
    ) -> None:
        self._repo = game_repo
        self._broadcaster = broadcaster
        self._engine = engine or GameEngine()

    async def create_game(
        self, host_name: str, user_id: str, max_players: int = 3
    ) -> Game:
        game = Game.create(max_players=max_players)
        host = Player.create(host_name, user_id=user_id)
        game.players.append(host)
        await self._repo.save(game)
        return game

    async def join_game(
        self, game_id: str, player_name: str, user_id: str
    ) -> tuple[Game, Player]:
        from app.domain.exceptions import InvalidActionError

        game = await self._repo.load(game_id)
        if game.status != GameStatus.LOBBY:
            raise InvalidActionError("Game is not in the lobby phase")
        if len(game.players) >= game.max_players:
            raise InvalidActionError("Game is already full")

        player = Player.create(player_name, user_id=user_id)
        game.players.append(player)
        await self._repo.save(game)

        await self._broadcaster.broadcast(
            game_id,
            [
                PlayerJoinedLobbyEvent(
                    game_id=game_id,
                    player_id=player.player_id,
                    player_name=player.name,
                    player_count=len(game.players),
                    max_players=game.max_players,
                )
            ],
            game,
        )

        if len(game.players) == game.max_players:
            await self.start_game(game_id)

        return game, player

    async def start_game(self, game_id: str, rng: Random | None = None) -> list[Event]:
        game = await self._repo.load(game_id)
        rng = rng or Random()
        new_game, events = self._engine.start_game(game, rng)
        await self._repo.save(new_game)
        await self._broadcaster.broadcast(game_id, events, new_game)
        return events

    async def handle_action(
        self, game_id: str, command: Command, rng: Random | None = None
    ) -> list[Event]:
        game = await self._repo.load(game_id)
        rng = rng or Random()
        new_game, events = self._engine.process(game, command, rng)
        await self._repo.save(new_game)
        await self._broadcaster.broadcast(game_id, events, new_game)
        return events

    async def get_game_state(self, game_id: str) -> GameStateResponse:
        game = await self._repo.load(game_id)
        return GameStateResponse.model_validate(game, from_attributes=True)

    def _game_to_dict(self, game: Game) -> dict:
        return dataclasses.asdict(game)
