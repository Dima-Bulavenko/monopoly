from typing import Protocol
from enum import StrEnum


class InboundMessagesNames(StrEnum): ...


class OutboundMessageNames(StrEnum):
    JOINED_GAME = "joined_game"


class IMessage(Protocol):
    type: InboundMessagesNames


class IMessageHandler(Protocol):
    async def handle(self, message: IMessage) -> None: ...


class IWebSocketSender(Protocol):
    """Push text messages to a specific WebSocket connection."""

    async def send(self, connection_id: str, text: str) -> None:
        """Send a text frame to a single connection."""

    async def close(self, connection_id: str, code: int = 1000) -> None:
        """Close a connection with the given WebSocket close code."""


class IWebSocketBroadcaster(Protocol):
    """Push text messages to multiple WebSocket connections."""

    async def broadcast(self, connection_ids: list[str], text: str) -> None:
        """Send a text frame to multiple connections."""


class IWebSocketHandler(Protocol):
    """React to WebSocket lifecycle events delivered by a transport adapter."""

    async def on_connect(self, connection_id: str, params: dict[str, str]) -> None:
        """A new client connection has been established.

        Args:
            connection_id: Opaque identifier for this connection.
            params: Raw query-string parameters supplied by the client
                    (e.g. ``{"token": "…"}``).
        """

    async def on_disconnect(self, connection_id: str) -> None:
        """A client connection has been closed or dropped."""

    async def on_message(self, connection_id: str, text: str) -> None:
        """A text frame has arrived from the client.

        Args:
            connection_id: Identifies which client sent the message.
            text: Raw message text — parsing is the handler's responsibility.
        """


class IWebSocketConnectionStore(Protocol):
    """Persist per-connection metadata (player ID, params) for the lifetime of a connection."""

    async def save(
        self, connection_id: str, user_id: str, params: dict[str, str]
    ) -> None:
        """Store metadata for a new connection."""

    async def load(self, connection_id: str) -> dict[str, str] | None:
        """Retrieve metadata for an existing connection.

        Returns:
            A dict containing at least ``{"user_id": "...", "params": {...}}``,
            or ``None`` if the connection is not found.
        """

    async def delete(self, connection_id: str) -> None:
        """Remove metadata for a closed connection."""

    async def connection_for_user(self, user_id: str) -> str | None:
        """Return the connection ID for a given user, or None if not connected."""
