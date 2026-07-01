from __future__ import annotations

from abc import ABC, abstractmethod


class WebSocketSender(ABC):
    """Push text messages to a specific WebSocket connection."""

    @abstractmethod
    async def send(self, connection_id: str, text: str) -> None:
        """Send a text frame to a single connection."""

    @abstractmethod
    async def close(self, connection_id: str, code: int = 1000) -> None:
        """Close a connection with the given WebSocket close code."""
