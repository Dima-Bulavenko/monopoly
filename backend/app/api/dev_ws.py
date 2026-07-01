"""FastAPI WebSocket transport adapter for local development.

This module is the **transport layer only** — it bridges FastAPI's WebSocket
lifecycle events to the application-level ``WebSocketAppHandler``.

Business logic lives in ``WebSocketAppHandler`` and the action callbacks
registered on it.  To add a new feature, register its action handlers at the
bottom of this file:

    from app.features.my_feature.ws import register_actions
    register_actions(_handler)
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.application.ws_handler import WebSocketAppHandler
from app.auth.infrastructure.jwt.rs256_service import make_verifier
from app.infrastructure.websocket.local_connection_store import InMemoryConnectionStore
from app.infrastructure.websocket.local_sender import (
    LocalConnectionRegistry,
    LocalWebSocketSender,
)

router = APIRouter(tags=["dev-websocket"])

# ---------------------------------------------------------------------------
# Process-level singletons (created once; shared across all connections).
# ---------------------------------------------------------------------------
_registry = LocalConnectionRegistry()
_sender = LocalWebSocketSender(_registry)
_store = InMemoryConnectionStore()
_handler = WebSocketAppHandler(
    sender=_sender,
    verifier=make_verifier(),
    store=_store,
)

# ---------------------------------------------------------------------------
# Register feature action handlers here.
# ---------------------------------------------------------------------------
# Example:
#   from app.features.game.ws_actions import register_game_actions
#   register_game_actions(_handler)


# ---------------------------------------------------------------------------
# Transport adapter — do not add business logic below this line.
# ---------------------------------------------------------------------------


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
