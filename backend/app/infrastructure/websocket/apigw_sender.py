"""AWS API Gateway Management API WebSocket sender for production."""

from __future__ import annotations

import aioboto3

from app.application.ports.websocket_sender import WebSocketSender
from app.config import settings


class ApiGatewayWebSocketSender(WebSocketSender):
    """Delivers text frames and connection-close requests via API Gateway Management API."""

    async def send(self, connection_id: str, text: str) -> None:
        session = aioboto3.Session()
        async with session.client(
            "apigatewaymanagementapi",
            endpoint_url=settings.apigw_management_endpoint,
            region_name=settings.aws_region,
        ) as apigw:
            try:
                await apigw.post_to_connection(
                    ConnectionId=connection_id,
                    Data=text.encode(),
                )
            except apigw.exceptions.GoneException:
                pass  # Connection already closed; caller may wish to clean up

    async def close(self, connection_id: str, code: int = 1000) -> None:
        """Force-close a connection via API Gateway.

        API Gateway does not expose a WebSocket close-code mechanism, so the
        *code* parameter is accepted for interface compatibility but not used.
        """
        session = aioboto3.Session()
        async with session.client(
            "apigatewaymanagementapi",
            endpoint_url=settings.apigw_management_endpoint,
            region_name=settings.aws_region,
        ) as apigw:
            try:
                await apigw.delete_connection(ConnectionId=connection_id)
            except apigw.exceptions.GoneException:
                pass
