"""Pydantic DTOs for WebSocket message envelopes."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class InboundMessage(BaseModel):
    """Message received from a WebSocket client."""

    action: str
    payload: dict[str, Any] = {}


class OutboundMessage(BaseModel):
    """Message broadcast to all clients in a game."""

    type: str
    events: list[dict[str, Any]] = []
    state: dict[str, Any] | None = None
    error: str | None = None


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str
