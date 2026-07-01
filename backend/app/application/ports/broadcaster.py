from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.game.events import Event
from app.domain.game.models import Game


class AbstractBroadcaster(ABC):
    @abstractmethod
    async def broadcast(
        self, game_id: str, events: list[Event], game: Game
    ) -> None: ...
