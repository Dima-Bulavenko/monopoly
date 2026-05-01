"""DynamoDB persistence for WebSocket connections.

Single-table design (two access patterns):
  PK = GAME#{game_id}   SK = CONNECTION#{connection_id}  → player_id, connected_at
  PK = CONNECTION#{connection_id}  SK = META             → game_id, player_id
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.infrastructure.db.dynamodb import TABLE_NAME, get_dynamodb_resource


class ConnectionRepository:
    async def save_connection(
        self, connection_id: str, game_id: str, player_id: str
    ) -> None:
        now = datetime.now(tz=timezone.utc).isoformat()
        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            # Forward record: game → connection
            await table.put_item(
                Item={
                    "PK": f"GAME#{game_id}",
                    "SK": f"CONNECTION#{connection_id}",
                    "player_id": player_id,
                    "connected_at": now,
                }
            )
            # Reverse record: connection → game (for disconnect lookup)
            await table.put_item(
                Item={
                    "PK": f"CONNECTION#{connection_id}",
                    "SK": "META",
                    "game_id": game_id,
                    "player_id": player_id,
                }
            )

    async def delete_connection(self, connection_id: str) -> None:
        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            # Look up game_id first
            resp = await table.get_item(
                Key={"PK": f"CONNECTION#{connection_id}", "SK": "META"}
            )
            meta = resp.get("Item")
            if meta:
                game_id = meta["game_id"]
                await table.delete_item(
                    Key={"PK": f"GAME#{game_id}", "SK": f"CONNECTION#{connection_id}"}
                )
                await table.delete_item(
                    Key={"PK": f"CONNECTION#{connection_id}", "SK": "META"}
                )

    async def list_connections_for_game(self, game_id: str) -> list[dict]:
        from boto3.dynamodb.conditions import Key

        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            resp = await table.query(
                KeyConditionExpression=(
                    Key("PK").eq(f"GAME#{game_id}")
                    & Key("SK").begins_with("CONNECTION#")
                )
            )
        return [
            {
                "connection_id": item["SK"].replace("CONNECTION#", ""),
                "player_id": item["player_id"],
            }
            for item in resp.get("Items", [])
        ]
