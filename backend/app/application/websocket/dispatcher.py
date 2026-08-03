from collections.abc import Mapping
from app.application.websocket.exceptions import UnknownMessageTypeError
from app.application.websocket.interfaces import IMessageHandler, IMessage


class MessageDispatcher:
    def __init__(
        self,
        handlers: Mapping[str, IMessageHandler] = {},
    ) -> None:
        self._handlers = dict(handlers)

    async def dispatch(self, message: IMessage) -> None:
        """Dispatch a message to the appropriate handler based on its type."""
        handler = self._handlers.get(message.type)

        if handler is None:
            raise UnknownMessageTypeError(message.type)

        await handler.handle(message)

    def register_handler(self, message_type: str, handler: IMessageHandler) -> None:
        """Register a new handler for a specific message type."""
        self._handlers[message_type] = handler
