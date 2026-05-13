"""DynamoDB persistence for Game state.

Single-table design:
  PK = GAME#{game_id}   SK = STATE
  Attribute 'version' is used for optimistic locking.
"""

from __future__ import annotations


from boto3.dynamodb.conditions import Attr

from app.domain.game.models import (
    AuctionState,
    Game,
    GameStatus,
    Player,
    PropertyState,
    TradeOffer,
    TradeStatus,
    TurnPhase,
)
from app.infrastructure.db.dynamodb import TABLE_NAME, get_dynamodb_resource


class GameNotFoundError(Exception):
    pass


class OptimisticLockError(Exception):
    pass


class GameRepository:
    async def load(self, game_id: str) -> Game:
        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            resp = await table.get_item(Key={"PK": f"GAME#{game_id}", "SK": "STATE"})
        item = resp.get("Item")
        if not item:
            raise GameNotFoundError(f"Game {game_id} not found")
        return self._deserialise(item)

    async def save(self, game: Game) -> None:
        item = self._serialise(game)
        prev_version = game.version
        game.version += 1
        item["version"] = game.version

        async with get_dynamodb_resource() as ddb:
            table = await ddb.Table(TABLE_NAME)
            try:
                if prev_version == 0:
                    # First save — item must not exist yet
                    await table.put_item(
                        Item=item,
                        ConditionExpression=Attr("PK").not_exists(),
                    )
                else:
                    await table.put_item(
                        Item=item,
                        ConditionExpression=Attr("version").eq(prev_version),
                    )
            except ddb.meta.client.exceptions.ConditionalCheckFailedException:
                raise OptimisticLockError(
                    f"Game {game.game_id} was modified concurrently"
                )

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def _serialise(self, game: Game) -> dict:
        return {
            "PK": f"GAME#{game.game_id}",
            "SK": "STATE",
            "game_id": game.game_id,
            "status": game.status.value,
            "phase": game.phase.value,
            "current_player_index": game.current_player_index,
            "free_parking_pot": game.free_parking_pot,
            "last_roll": list(game.last_roll),
            "community_chest_deck": game.community_chest_deck,
            "chance_deck": game.chance_deck,
            "players": [self._serialise_player(p) for p in game.players],
            "properties": {
                str(k): self._serialise_property(v) for k, v in game.properties.items()
            },
            "pending_auction": self._serialise_auction(game.pending_auction),
            "pending_trade": self._serialise_trade(game.pending_trade),
            "max_players": game.max_players,
            "version": game.version,
        }

    def _serialise_player(self, p: Player) -> dict:
        return {
            "player_id": p.player_id,
            "name": p.name,
            "position": p.position,
            "balance": p.balance,
            "in_jail": p.in_jail,
            "jail_turns": p.jail_turns,
            "consecutive_doubles": p.consecutive_doubles,
            "get_out_of_jail_cards": p.get_out_of_jail_cards,
            "is_bankrupt": p.is_bankrupt,
        }

    def _serialise_property(self, prop: PropertyState) -> dict:
        return {
            "square_index": prop.square_index,
            "owner_id": prop.owner_id,
            "houses": prop.houses,
            "hotel": prop.hotel,
            "mortgaged": prop.mortgaged,
        }

    def _serialise_auction(self, auction: AuctionState | None) -> dict | None:
        if auction is None:
            return None
        return {
            "property_index": auction.property_index,
            "bids": auction.bids,
            "passed_player_ids": auction.passed_player_ids,
            "current_bidder_index": auction.current_bidder_index,
        }

    def _serialise_trade(self, trade: TradeOffer | None) -> dict | None:
        if trade is None:
            return None
        return {
            "trade_id": trade.trade_id,
            "proposer_id": trade.proposer_id,
            "target_id": trade.target_id,
            "offer_property_indices": trade.offer_property_indices,
            "offer_money": trade.offer_money,
            "request_property_indices": trade.request_property_indices,
            "request_money": trade.request_money,
            "status": trade.status.value,
        }

    def _deserialise(self, item: dict) -> Game:
        game = Game(
            game_id=item["game_id"],
            status=GameStatus(item["status"]),
            phase=TurnPhase(item["phase"]),
            current_player_index=int(item["current_player_index"]),
            free_parking_pot=int(item["free_parking_pot"]),
            last_roll=(int(item["last_roll"][0]), int(item["last_roll"][1])),
            community_chest_deck=item["community_chest_deck"],
            chance_deck=item["chance_deck"],
            max_players=int(item.get("max_players", 2)),
            version=int(item.get("version", 0)),
        )
        game.players = [self._deserialise_player(p) for p in item["players"]]
        game.properties = {
            int(k): self._deserialise_property(v) for k, v in item["properties"].items()
        }
        if item.get("pending_auction"):
            game.pending_auction = self._deserialise_auction(item["pending_auction"])
        if item.get("pending_trade"):
            game.pending_trade = self._deserialise_trade(item["pending_trade"])
        return game

    def _deserialise_player(self, d: dict) -> Player:
        return Player(
            player_id=d["player_id"],
            name=d["name"],
            position=int(d["position"]),
            balance=int(d["balance"]),
            in_jail=bool(d["in_jail"]),
            jail_turns=int(d["jail_turns"]),
            consecutive_doubles=int(d["consecutive_doubles"]),
            get_out_of_jail_cards=int(d["get_out_of_jail_cards"]),
            is_bankrupt=bool(d["is_bankrupt"]),
        )

    def _deserialise_property(self, d: dict) -> PropertyState:
        return PropertyState(
            square_index=int(d["square_index"]),
            owner_id=d.get("owner_id"),
            houses=int(d["houses"]),
            hotel=bool(d["hotel"]),
            mortgaged=bool(d["mortgaged"]),
        )

    def _deserialise_auction(self, d: dict) -> AuctionState:
        return AuctionState(
            property_index=int(d["property_index"]),
            bids={k: int(v) for k, v in d["bids"].items()},
            passed_player_ids=d["passed_player_ids"],
            current_bidder_index=int(d["current_bidder_index"]),
        )

    def _deserialise_trade(self, d: dict) -> TradeOffer:
        return TradeOffer(
            trade_id=d["trade_id"],
            proposer_id=d["proposer_id"],
            target_id=d["target_id"],
            offer_property_indices=d["offer_property_indices"],
            offer_money=int(d["offer_money"]),
            request_property_indices=d["request_property_indices"],
            request_money=int(d["request_money"]),
            status=TradeStatus(d["status"]),
        )
