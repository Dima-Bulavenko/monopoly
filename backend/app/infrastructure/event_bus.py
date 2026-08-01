from collections import defaultdict
from collections.abc import Awaitable, Callable
from app.application.websocket.messages import OutboundMessages


class InMemoryEventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    async def publish(self, event: OutboundMessages) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler(event)

    def subscribe(
        self,
        event: OutboundMessages,
        handler: Callable[[OutboundMessages], Awaitable[None]],
    ) -> None:
        event_type = type(event)
        self._handlers[event_type].append(handler)
