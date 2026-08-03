from app.config import settings
from app.config import EnvOptions
from app.infrastructure.event_bus import InMemoryEventBus
from app.application.event_bus import IEventBus
from app.application.websocket.interfaces import (
    IWebSocketSender,
    IWebSocketBroadcaster,
    IWebSocketConnectionStore,
)
from app.application.websocket.dispatcher import MessageDispatcher


def make_event_bus() -> IEventBus:
    """Create an instance of the event bus."""
    if settings.env == EnvOptions.LOCAL:
        return InMemoryEventBus()
    raise NotImplementedError(
        f"Event bus not implemented for {settings.env} environment."
    )


def make_sender() -> IWebSocketSender:
    if settings.env == EnvOptions.LOCAL:
        from app.infrastructure.websocket.local_sender import LocalWebSocketSender

        return LocalWebSocketSender()
    raise NotImplementedError(
        f"WebSocket sender not implemented for {settings.env} environment."
    )


def make_broadcaster(sender: IWebSocketSender) -> IWebSocketBroadcaster:
    if settings.env == EnvOptions.LOCAL:
        from app.infrastructure.websocket.local_sender import LocalWebSocketBroadcaster

        return LocalWebSocketBroadcaster(sender)
    raise NotImplementedError(
        f"WebSocket broadcaster not implemented for {settings.env} environment."
    )


def make_connection_store() -> IWebSocketConnectionStore:
    if settings.env == EnvOptions.LOCAL:
        from app.infrastructure.websocket.local_store import LocalConnectionStore

        return LocalConnectionStore()
    raise NotImplementedError(
        f"WebSocket connection store not implemented for {settings.env} environment."
    )


def make_dispatcher() -> MessageDispatcher:
    return MessageDispatcher()


class Container:
    def __init__(self) -> None:
        self._event_bus = None
        self._sender = None
        self._broadcaster = None
        self._connection_store = None

    @property
    def event_bus(self) -> IEventBus:
        if self._event_bus is None:
            self._event_bus = make_event_bus()
        return self._event_bus

    @property
    def sender(self) -> IWebSocketSender:
        if self._sender is None:
            self._sender = make_sender()
        return self._sender

    @property
    def broadcaster(self) -> IWebSocketBroadcaster:
        if self._broadcaster is None:
            self._broadcaster = make_broadcaster(self.sender)
        return self._broadcaster

    @property
    def connection_store(self) -> IWebSocketConnectionStore:
        if self._connection_store is None:
            self._connection_store = make_connection_store()
        return self._connection_store

    @property
    def dispatcher(self) -> MessageDispatcher:
        return make_dispatcher()


def register_websocket_event_handlers(container: Container) -> None:
    """Subscribe application event handlers to the event bus.

    Must be called once during app startup.
    """
    from app.application.websocket.handlers.joined_game import JoinedGameHandler
    from app.application.websocket.messages import JoinedGameMessage
    from app.infrastructure.db.game_repository import GameRepository

    joined_game_handler = JoinedGameHandler(
        broadcaster=container.broadcaster,
        store=container.connection_store,
        game_repo=GameRepository(),
    )
    container.event_bus.subscribe(JoinedGameMessage, joined_game_handler.handle)


container = Container()
