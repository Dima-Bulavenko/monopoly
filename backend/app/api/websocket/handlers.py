"""AWS Lambda handlers for API Gateway WebSocket routes.

Route selection expression: $request.body.action

Routes:
  $connect      → connect_handler
  $disconnect   → disconnect_handler
  *             → action_handler   (all game actions)
"""

from __future__ import annotations

import json

from app.application.connection_service import ConnectionService
from app.application.dto.websocket_dto import InboundMessage
from app.application.game_service import GameService
from app.domain.exceptions import DomainError
from app.domain.game.commands import (
    AcceptTradeCommand,
    AuctionBidCommand,
    AuctionPassCommand,
    BuyPropertyCommand,
    BuildHotelCommand,
    BuildHouseCommand,
    DeclareBankruptcyCommand,
    EndTurnCommand,
    MortgagePropertyCommand,
    PassPropertyCommand,
    PayJailFineCommand,
    ProposeTradeCommand,
    RejectTradeCommand,
    RollDiceCommand,
    SellHotelCommand,
    SellHouseCommand,
    UnmortgagePropertyCommand,
    UseJailCardCommand,
)
from app.infrastructure.db.connection_repository import ConnectionRepository
from app.infrastructure.db.game_repository import GameNotFoundError, GameRepository
from app.infrastructure.websocket.broadcaster import WebSocketBroadcaster


def _make_services() -> tuple[GameService, ConnectionService]:
    repo = GameRepository()
    conn_repo = ConnectionRepository()
    broadcaster = WebSocketBroadcaster(conn_repo)
    game_svc = GameService(repo, broadcaster)
    conn_svc = ConnectionService(conn_repo)
    return game_svc, conn_svc


def _ok(body: dict | None = None) -> dict:
    return {"statusCode": 200, "body": json.dumps(body or {})}


def _err(code: int, message: str) -> dict:
    return {"statusCode": code, "body": json.dumps({"error": message})}


async def connect_handler(event: dict, context: object) -> dict:
    """$connect route — store connection → (game_id, player_id) mapping."""
    query = event.get("queryStringParameters") or {}
    game_id = query.get("game_id")
    player_id = query.get("player_id")

    if not game_id or not player_id:
        return _err(400, "game_id and player_id query params are required")

    conn_id = event["requestContext"]["connectionId"]
    _, conn_svc = _make_services()
    await conn_svc.on_connect(conn_id, game_id, player_id)
    return _ok()


async def disconnect_handler(event: dict, context: object) -> dict:
    """$disconnect route — remove connection record."""
    conn_id = event["requestContext"]["connectionId"]
    _, conn_svc = _make_services()
    await conn_svc.on_disconnect(conn_id)
    return _ok()


async def action_handler(event: dict, context: object) -> dict:
    """Default route — receives all game action messages."""
    conn_id = event["requestContext"]["connectionId"]

    try:
        body = json.loads(event.get("body") or "{}")
        msg = InboundMessage(**body)
    except Exception:
        return _err(400, "Invalid message format")

    # Resolve game_id and player_id from connection store
    from app.infrastructure.db.dynamodb import TABLE_NAME, get_dynamodb_resource

    async with get_dynamodb_resource() as ddb:
        table = await ddb.Table(TABLE_NAME)
        resp = await table.get_item(Key={"PK": f"CONNECTION#{conn_id}", "SK": "META"})
    meta = resp.get("Item")
    if not meta:
        return _err(403, "Unknown connection")

    game_id: str = meta["game_id"]
    player_id: str = meta["player_id"]

    try:
        command = _build_command(msg.action, player_id, msg.payload)
    except (KeyError, ValueError) as exc:
        return _err(400, f"Bad payload: {exc}")

    game_svc, _ = _make_services()
    try:
        await game_svc.handle_action(game_id, command)
    except GameNotFoundError:
        return _err(404, "Game not found")
    except DomainError as exc:
        return _err(422, str(exc))

    return _ok()


def _build_command(action: str, player_id: str, payload: dict):
    match action:
        case "roll_dice":
            return RollDiceCommand(player_id=player_id)
        case "buy_property":
            return BuyPropertyCommand(player_id=player_id)
        case "pass_property":
            return PassPropertyCommand(player_id=player_id)
        case "auction_bid":
            return AuctionBidCommand(player_id=player_id, amount=int(payload["amount"]))
        case "auction_pass":
            return AuctionPassCommand(player_id=player_id)
        case "end_turn":
            return EndTurnCommand(player_id=player_id)
        case "build_house":
            return BuildHouseCommand(
                player_id=player_id, property_index=int(payload["property_index"])
            )
        case "sell_house":
            return SellHouseCommand(
                player_id=player_id, property_index=int(payload["property_index"])
            )
        case "build_hotel":
            return BuildHotelCommand(
                player_id=player_id, property_index=int(payload["property_index"])
            )
        case "sell_hotel":
            return SellHotelCommand(
                player_id=player_id, property_index=int(payload["property_index"])
            )
        case "mortgage_property":
            return MortgagePropertyCommand(
                player_id=player_id, property_index=int(payload["property_index"])
            )
        case "unmortgage_property":
            return UnmortgagePropertyCommand(
                player_id=player_id, property_index=int(payload["property_index"])
            )
        case "pay_jail_fine":
            return PayJailFineCommand(player_id=player_id)
        case "use_jail_card":
            return UseJailCardCommand(player_id=player_id)
        case "propose_trade":
            return ProposeTradeCommand(
                player_id=player_id,
                target_player_id=payload["target_player_id"],
                offer_property_indices=tuple(payload.get("offer_property_indices", [])),
                offer_money=int(payload.get("offer_money", 0)),
                request_property_indices=tuple(
                    payload.get("request_property_indices", [])
                ),
                request_money=int(payload.get("request_money", 0)),
            )
        case "accept_trade":
            return AcceptTradeCommand(player_id=player_id, trade_id=payload["trade_id"])
        case "reject_trade":
            return RejectTradeCommand(player_id=player_id, trade_id=payload["trade_id"])
        case "declare_bankruptcy":
            return DeclareBankruptcyCommand(player_id=player_id)
        case _:
            raise ValueError(f"Unknown action: {action}")
