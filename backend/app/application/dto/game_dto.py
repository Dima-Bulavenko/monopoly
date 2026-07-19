"""Pydantic DTOs for HTTP endpoints."""

from __future__ import annotations
from typing import Annotated

from pydantic import BaseModel, Field

from app.domain.game.models import (
    Game,
    GameStatus,
    TurnPhase,
    Player,
    PropertyState,
    TradeOffer,
    AuctionState,
)


class CreateGameDTO(BaseModel):
    max_players: Annotated[int,Field(ge=2, le=6)]


class ReadGameDTO(BaseModel):
    game_id: str


class GameStateResponse(BaseModel):
    """A strict representation of the `Game` domain state suitable for HTTP responses.

    Types mirror the domain models where appropriate (enums and pydantic models).
    Note: JSON object keys for `properties` will be strings in transport, but the
    domain expects integer indices; Pydantic will coerce when parsing.
    """

    game_id: str
    status: GameStatus
    phase: TurnPhase
    current_player_index: int | None
    players: list[Player]
    properties: dict[int, PropertyState]
    free_parking_pot: int
    max_players: int
    pending_trade: TradeOffer | None = None
    pending_auction: AuctionState | None = None
    last_roll: tuple[int, int] = (0, 0)
    version: int = 0
