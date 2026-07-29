from __future__ import annotations

import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.application.ws_handler import WebSocketAppHandler
from app.auth.infrastructure.jwt.rs256_service import make_verifier
from app.infrastructure.websocket.local_sender import (
    LocalConnectionRegistry,
    LocalWebSocketSender,
)
from app.infrastructure.websocket.local_store import LocalConnectionStore
from app.application.websocket.dispatcher import MessageDispatcher

router = APIRouter(tags=["dev-websocket"])

_registry = LocalConnectionRegistry()
_sender = LocalWebSocketSender(_registry)
_store = LocalConnectionStore()
_handler = WebSocketAppHandler(
    sender=_sender,
    verifier=make_verifier(),
    store=_store,
    dispatcher=MessageDispatcher(handlers={}),
)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    """Accept a WebSocket connection and drive the application handler."""
    connection_id = str(uuid.uuid4())
    params: dict[str, str] = dict(ws.query_params)

    await ws.accept()
    _registry.register(connection_id, ws)

    try:
        await _handler.on_connect(connection_id, params)
        async for text in ws.iter_text():
            await _handler.on_message(connection_id, text)
    except WebSocketDisconnect:
        pass
    finally:
        await _handler.on_disconnect(connection_id)
        _registry.unregister(connection_id)
