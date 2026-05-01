"""Application service orchestrating the game engine with persistence and broadcasting."""

from __future__ import annotations

import dataclasses
from random import Random
from typing import TYPE_CHECKING

from app.domain.game.commands import Command
from app.domain.game.engine import GameEngine
from app.domain.game.events import Event
from app.domain.game.models import Game, Player

if TYPE_CHECKING:
    from app.infrastructure.db.game_repository import GameRepository
    from app.infrastructure.websocket.broadcaster import WebSocketBroadcaster


class GameService:
    def __init__(
        self,
        game_repo: "GameRepository",
        broadcaster: "WebSocketBroadcaster",
        engine: GameEngine | None = None,
    ) -> None:
        self._repo = game_repo
        self._broadcaster = broadcaster
        self._engine = engine or GameEngine()

    async def create_game(self, host_name: str) -> Game:
        game = Game.create()
        host = Player.create(host_name)
        game.players.append(host)
        await self._repo.save(game)
        return game

    async def join_game(self, game_id: str, player_name: str) -> tuple[Game, Player]:
        game = await self._repo.load(game_id)
        player = Player.create(player_name)
        game.players.append(player)
        await self._repo.save(game)
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

    async def get_game_state(self, game_id: str) -> Game:
        return await self._repo.load(game_id)

    def _game_to_dict(self, game: Game) -> dict:
        return dataclasses.asdict(game)
