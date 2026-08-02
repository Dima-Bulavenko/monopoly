from collections.abc import Awaitable, Callable
from typing import Protocol
from app.application.websocket.messages import OutboundMessages


class IEventBus(Protocol):
    """Publish events to subscribers."""

    async def publish(self, event: OutboundMessages) -> None:
        """Publish an event to all subscribers."""

    def subscribe[T: OutboundMessages](
        self, event_type: type[T], handler: Callable[[T], Awaitable[None]]
    ) -> None:
        """Subscribe a handler to a specific event type."""
