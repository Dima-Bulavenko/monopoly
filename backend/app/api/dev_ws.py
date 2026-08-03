from __future__ import annotations
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.application.ws_handler import WebSocketAppHandler
from app.auth.infrastructure.jwt.rs256_service import make_verifier
from app.infrastructure.websocket.local_sender import (
    local_registry as _registry,
)
from app.bootstrap import container

router = APIRouter(tags=["dev-websocket"])


_handler = WebSocketAppHandler(
    verifier=make_verifier(),
    sender=container.sender,
    store=container.connection_store,
    dispatcher=container.dispatcher,
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
