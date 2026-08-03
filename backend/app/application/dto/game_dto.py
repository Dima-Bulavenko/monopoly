"""Pydantic DTOs for HTTP endpoints."""

from __future__ import annotations
from typing import Annotated

from pydantic import BaseModel, Field
from app.domain.game.models import Player


class CreateGameDTO(BaseModel):
    max_players: Annotated[int, Field(ge=2, le=6)]


class ReadGameDTO(BaseModel):
    game_id: str
    players: list[Player]
    max_players: Annotated[int, Field(ge=2, le=6)]
