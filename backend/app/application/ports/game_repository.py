from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.game.models import Game


class AbstractGameRepository(ABC):
    @abstractmethod
    async def get(self, game_id: str) -> Game | None:
        """Retrieve a game by ID. Returns None if not found."""
        ...

    @abstractmethod
    async def update(self, game: Game) -> Game:
        """Update an existing game. Raises GameNotFoundError if game does not exist."""
        ...

    @abstractmethod
    async def create(self, game: Game) -> Game:
        """Create a new game. Raises GameAlreadyExistsError if game already exists."""
        ...
