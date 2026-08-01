from collections.abc import Awaitable, Callable
from typing import Protocol
from app.application.websocket.messages import OutboundMessages


class EventBus[T: OutboundMessages](Protocol):
    """Publish events to subscribers."""

    async def publish(self, event: T) -> None:
        """Publish an event to all subscribers."""

    def subscribe(self, event: T, handler: Callable[[T], Awaitable[None]]) -> None:
        """Subscribe a handler to a specific event type."""
