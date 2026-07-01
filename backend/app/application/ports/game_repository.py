from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.game.models import Game


class AbstractGameRepository(ABC):
    @abstractmethod
    async def load(self, game_id: str) -> Game: ...

    @abstractmethod
    async def save(self, game: Game) -> None: ...
