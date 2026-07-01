from __future__ import annotations

from abc import ABC, abstractmethod


class WebSocketHandler(ABC):
    """React to WebSocket lifecycle events delivered by a transport adapter."""

    @abstractmethod
    async def on_connect(self, connection_id: str, params: dict[str, str]) -> None:
        """A new client connection has been established.

        Args:
            connection_id: Opaque identifier for this connection.
            params: Raw query-string parameters supplied by the client
                    (e.g. ``{"game_id": "…", "token": "…"}``).
        """

    @abstractmethod
    async def on_disconnect(self, connection_id: str) -> None:
        """A client connection has been closed or dropped."""

    @abstractmethod
    async def on_message(self, connection_id: str, text: str) -> None:
        """A text frame has arrived from the client.

        Args:
            connection_id: Identifies which client sent the message.
            text: Raw message text — parsing is the handler's responsibility.
        """
