"""DynamoDB-backed WebSocket connection store for production."""

from __future__ import annotations

from app.application.ports.connection_store import (
    AbstractConnectionStore,
    ConnectionMeta,
)
from typing import cast
from app.infrastructure.db.dynamodb import TABLE_NAME, get_dynamodb_resource


class DynamoDbConnectionStore(AbstractConnectionStore):
    """Persists connection metadata in DynamoDB using a single-table design.

    Access pattern::

        PK = CONNECTION#{connection_id}   SK = META
            → user_id, params (dict stored as a DynamoDB map)
    """

    async def save(
        self,
        connection_id: str,
        user_id: str,
        params: dict[str, str],
    ) -> None:
        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            await table.put_item(
                Item={
                    "PK": f"CONNECTION#{connection_id}",
                    "SK": "META",
                    "user_id": user_id,
                    "params": params,
                }
            )

    async def load(self, connection_id: str) -> ConnectionMeta | None:
        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            resp = await table.get_item(
                Key={"PK": f"CONNECTION#{connection_id}", "SK": "META"}
            )
        item = resp.get("Item")
        if item is None:
            return None
        return ConnectionMeta(
            user_id=str(item["user_id"]),
            params=cast(dict[str, str], item.get("params", {})),
        )

    async def delete(self, connection_id: str) -> None:
        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            await table.delete_item(
                Key={"PK": f"CONNECTION#{connection_id}", "SK": "META"}
            )
