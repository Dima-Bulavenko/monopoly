"""Concrete WebSocket application handler — generic, feature-agnostic dispatcher.

Usage
-----
Build one handler per process startup and register action callbacks for every
feature that needs WebSocket support:

    handler = WebSocketAppHandler(sender, verifier, store)
    handler.register("roll_dice", game_feature.handle_roll_dice)
    handler.register("chat_message", chat_feature.handle_message)

The transport adapter (FastAPI endpoint or Lambda function) then calls
``on_connect``, ``on_message``, and ``on_disconnect`` on the handler.

Message format (inbound)::

    {"action": "<registered_action>", "payload": {...}}

A missing or unrecognised action is silently ignored so that the wire protocol
can evolve without breaking older clients.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from app.application.ports.websocket_handler import WebSocketHandler

if TYPE_CHECKING:
    from app.application.ports.connection_store import AbstractConnectionStore
    from app.application.ports.websocket_sender import WebSocketSender
    from app.auth.domain.token_service import JWTVerifier

logger = logging.getLogger(__name__)

# Signature: (connection_id, user_id, payload) → None
ActionHandler = Callable[[str, str, dict], Awaitable[None]]

_CLOSE_UNAUTHORIZED = 4001
_CLOSE_NORMAL = 1000


class WebSocketAppHandler(WebSocketHandler):
    """Generic, feature-agnostic WebSocket handler.

    * Authenticates each connection using a JWT from the ``token`` query param.
    * Stores per-connection metadata (player ID, params) via ``AbstractConnectionStore``.
    * Dispatches inbound text frames to registered action handlers.
    """

    def __init__(
        self,
        sender: "WebSocketSender",
        verifier: "JWTVerifier",
        store: "AbstractConnectionStore",
    ) -> None:
        self._sender = sender
        self._verifier = verifier
        self._store = store
        self._handlers: dict[str, ActionHandler] = {}

    async def on_connect(self, connection_id: str, params: dict[str, str]) -> None:
        token = params.pop("token", "")
        try:
            claims = self._verifier.verify(token)
        except ValueError:
            logger.warning(
                "WebSocket connect rejected — invalid token (conn=%s)", connection_id
            )
            await self._sender.close(connection_id, code=_CLOSE_UNAUTHORIZED)
            return

        user_id: str = claims["sub"]
        await self._store.save(connection_id, user_id, params)
        logger.debug("WebSocket connected: conn=%s user=%s", connection_id, user_id)

    async def on_disconnect(self, connection_id: str) -> None:
        await self._store.delete(connection_id)
        logger.debug("WebSocket disconnected: conn=%s", connection_id)

    async def on_message(self, connection_id: str, text: str) -> None:
        meta = await self._store.load(connection_id)
        if meta is None:
            # Connection not in store — unauthenticated or already closed.
            await self._sender.close(connection_id, code=_CLOSE_UNAUTHORIZED)
            return
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("WebSocket bad JSON from conn=%s", connection_id)
            return

        if not isinstance(body, dict):
            return

        action: str = body.get("action", "")
        payload: dict = (
            body.get("payload", {}) if isinstance(body.get("payload"), dict) else {}
        )

        handler = self._handlers.get(action)
        if handler is None:
            logger.debug(
                "WebSocket unknown action %r from conn=%s", action, connection_id
            )
            return

        try:
            await handler(connection_id, meta["user_id"], payload)
        except Exception:
            logger.exception(
                "WebSocket action handler error: action=%r conn=%s",
                action,
                connection_id,
            )
