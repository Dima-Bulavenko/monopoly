"""DynamoDB persistence for Game state.

Single-table design:
  PK = GAME#{game_id}   SK = STATE
  Attribute 'version' is used for optimistic locking.
"""

from __future__ import annotations


from boto3.dynamodb.conditions import Attr

from app.domain.game.models import (
    Game,
)
from app.application.ports.game_repository import AbstractGameRepository
from app.infrastructure.db.dynamodb import TABLE_NAME, get_dynamodb_resource
from app.domain.game.exceptions import GameAlreadyExistsError, GameNotFoundError


class GameRepository(AbstractGameRepository):
    async def get(self, game_id: str) -> Game | None:
        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            resp = await table.get_item(Key=self.__get_key(game_id))
        item = resp.get("Item")
        return Game.model_validate(item, from_attributes=True) if item else None

    async def create(self, game: Game) -> Game:
        """Create a new game in DynamoDB. Raises GameAlreadyExistsError if game already exists."""
        item = self.__serialize(game)

        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            try:
                await table.put_item(
                    Item=item,
                    ConditionExpression=Attr("PK").not_exists(),
                )
            except ddb.meta.client.exceptions.ConditionalCheckFailedException:
                raise GameAlreadyExistsError(
                    f"Game with ID {game.game_id} already exists"
                )

        return game

    async def update(self, game: Game) -> Game:
        item = self.__serialize(game)

        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            try:
                await table.put_item(
                    Item=item,
                    ConditionExpression=Attr("PK").exists(),
                )
            except ddb.meta.client.exceptions.ConditionalCheckFailedException:
                raise GameNotFoundError(f"Game with ID {game.game_id} not found")

        return game

    def __get_key(self, game_id: str) -> dict:
        return {"PK": f"GAME#{game_id}", "SK": "STATE"}

    def __serialize(self, game: Game) -> dict:
        """Serialize a Game object to a DynamoDB item."""
        return {**self.__get_key(game.game_id), **game.model_dump(mode="json")}
