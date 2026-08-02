from collections import defaultdict
from collections.abc import Awaitable, Callable
from app.application.websocket.messages import OutboundMessages


class InMemoryEventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    async def publish(self, event: OutboundMessages) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler(event)

    def subscribe[T: OutboundMessages](
        self,
        event_type: type[T],
        handler: Callable[[T], Awaitable[None]],
    ) -> None:
        self._handlers[event_type].append(handler)
