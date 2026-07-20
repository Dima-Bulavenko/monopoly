"""Pydantic DTOs for HTTP endpoints."""

from __future__ import annotations
from typing import Annotated

from pydantic import BaseModel, Field


class CreateGameDTO(BaseModel):
    max_players: Annotated[int, Field(ge=2, le=6)]


class ReadGameDTO(BaseModel):
    game_id: str
