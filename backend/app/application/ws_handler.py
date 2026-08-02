from __future__ import annotations

import json
import logging

from app.application.websocket.interfaces import (
    IWebSocketHandler,
    IWebSocketSender,
    IWebSocketConnectionStore,
)
from app.auth.domain.token_service import IJWTVerifier
from app.application.websocket.messages import inbound_messages_adapter
from pydantic import ValidationError
from app.application.websocket.dispatcher import MessageDispatcher

logger = logging.getLogger(__name__)

_CLOSE_UNAUTHORIZED = 4001
_CLOSE_NORMAL = 1000


class WebSocketAppHandler(IWebSocketHandler):
    """Generic, feature-agnostic WebSocket handler.

    * Authenticates each connection using a JWT from the ``token`` query param.
    * Stores per-connection metadata (player ID, params) via ``AbstractConnectionStore``.
    * Dispatches inbound text frames to registered action handlers.
    """

    def __init__(
        self,
        sender: IWebSocketSender,
        verifier: IJWTVerifier,
        store: IWebSocketConnectionStore,
        dispatcher: MessageDispatcher,
    ) -> None:
        self._sender = sender
        self._verifier = verifier
        self._store = store
        self._dispatcher = dispatcher

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

        try:
            message = inbound_messages_adapter.validate_python(body)
        except ValidationError as e:
            logger.warning(
                "WebSocket invalid message from conn=%s: %s", connection_id, e
            )
            return

        await self._dispatcher.dispatch(message)
