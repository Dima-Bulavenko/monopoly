"""Pydantic DTOs for HTTP endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateGameRequest(BaseModel):
    host_name: str = Field(..., min_length=1, max_length=50)


class JoinGameRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)


class GameResponse(BaseModel):
    game_id: str
    status: str
    player_count: int


class GameStateResponse(BaseModel):
    game_id: str
    status: str
    phase: str
    current_player_id: str | None
    players: list[dict]
    properties: dict[str, dict]
    free_parking_pot: int
