"""In-process WebSocket sender and connection registry for local development.

Production uses API Gateway to manage connections; locally, FastAPI WebSocket
endpoints register themselves in ``LocalConnectionRegistry`` and
``LocalWebSocketSender`` delivers frames directly — no AWS required.
"""

from __future__ import annotations

from fastapi import WebSocket

from app.application.websocket.interfaces import WebSocketBroadcaster, WebSocketSender


class LocalConnectionRegistry:
    """Thread-safe (asyncio) map of connection ID → live FastAPI WebSocket."""

    def __init__(self) -> None:
        self._sockets: dict[str, WebSocket] = {}

    def register(self, connection_id: str, ws: WebSocket) -> None:
        self._sockets[connection_id] = ws

    def unregister(self, connection_id: str) -> None:
        self._sockets.pop(connection_id, None)

    def get(self, connection_id: str) -> WebSocket | None:
        return self._sockets.get(connection_id)


# Singleton shared between the router and the sender.
local_registry = LocalConnectionRegistry()


class LocalWebSocketBroadcaster(WebSocketBroadcaster):
    """Broadcasts text frames to multiple connections via the local registry."""

    def __init__(self, sender: LocalWebSocketSender) -> None:
        self._sender = sender

    async def broadcast(self, connection_ids: list[str], text: str) -> None:
        for connection_id in connection_ids:
            await self._sender.send(connection_id, text)


class LocalWebSocketSender(WebSocketSender):
    """Delivers text frames directly to the registered FastAPI WebSocket."""

    def __init__(self, registry: LocalConnectionRegistry = local_registry) -> None:
        self._registry = registry

    async def send(self, connection_id: str, text: str) -> None:
        ws = self._registry.get(connection_id)
        if ws is not None:
            await ws.send_text(text)

    async def close(self, connection_id: str, code: int = 1000) -> None:
        ws = self._registry.get(connection_id)
        if ws is not None:
            try:
                await ws.close(code=code)
            finally:
                self._registry.unregister(connection_id)
