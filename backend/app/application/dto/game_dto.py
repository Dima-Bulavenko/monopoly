"""Pydantic DTOs for HTTP endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateGameRequest(BaseModel):
    max_players: int = Field(default=3, ge=2, le=6)


class GameResponse(BaseModel):
    game_id: str
    status: str
    player_count: int
    max_players: int


class GameStateResponse(BaseModel):
    game_id: str
    status: str
    phase: str
    current_player_id: str | None
    players: list[dict]
    properties: dict[str, dict]
    free_parking_pot: int
    max_players: int
