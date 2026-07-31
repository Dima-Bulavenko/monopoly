from collections import defaultdict
from typing import Callable
from app.application.websocket.messages import OutboundMessages


class InMemoryEventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    async def publish(self, event: OutboundMessages) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)

    def subscribe(
        self,
        event: OutboundMessages,
        handler: Callable[[OutboundMessages], None],
    ) -> None:
        event_type = type(event)
        self._handlers[event_type].append(handler)
