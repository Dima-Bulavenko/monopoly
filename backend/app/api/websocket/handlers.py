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
from app.application.dto.websocket_dto import (
    AcceptTradeMessage,
    AuctionBidMessage,
    AuctionPassMessage,
    BuyPropertyMessage,
    BuildHotelMessage,
    BuildHouseMessage,
    DeclareBankruptcyMessage,
    EndTurnMessage,
    InboundAdapter,
    MortgagePropertyMessage,
    PassPropertyMessage,
    PayJailFineMessage,
    ProposeTradeMessage,
    RejectTradeMessage,
    RollDiceMessage,
    SellHotelMessage,
    SellHouseMessage,
    UnmortgagePropertyMessage,
    UseJailCardMessage,
)
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
    token = query.get("token")

    if not game_id or not token:
        return _err(400, "game_id and token query params are required")

    from app.auth.infrastructure.jwt.rs256_service import make_verifier

    try:
        payload = make_verifier().verify(token)
    except ValueError as exc:
        return _err(401, str(exc))

    player_id: str = payload["sub"]
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
        msg = InboundAdapter.validate_python(body)
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
        command = _build_command(msg, player_id)
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


def _build_command(msg: object, player_id: str):  # noqa: PLR0911
    match msg:
        case RollDiceMessage():
            return RollDiceCommand(player_id=player_id)
        case BuyPropertyMessage():
            return BuyPropertyCommand(player_id=player_id)
        case PassPropertyMessage():
            return PassPropertyCommand(player_id=player_id)
        case AuctionBidMessage():
            return AuctionBidCommand(player_id=player_id, amount=msg.amount)
        case AuctionPassMessage():
            return AuctionPassCommand(player_id=player_id)
        case EndTurnMessage():
            return EndTurnCommand(player_id=player_id)
        case BuildHouseMessage():
            return BuildHouseCommand(
                player_id=player_id, property_index=msg.property_index
            )
        case SellHouseMessage():
            return SellHouseCommand(
                player_id=player_id, property_index=msg.property_index
            )
        case BuildHotelMessage():
            return BuildHotelCommand(
                player_id=player_id, property_index=msg.property_index
            )
        case SellHotelMessage():
            return SellHotelCommand(
                player_id=player_id, property_index=msg.property_index
            )
        case MortgagePropertyMessage():
            return MortgagePropertyCommand(
                player_id=player_id, property_index=msg.property_index
            )
        case UnmortgagePropertyMessage():
            return UnmortgagePropertyCommand(
                player_id=player_id, property_index=msg.property_index
            )
        case PayJailFineMessage():
            return PayJailFineCommand(player_id=player_id)
        case UseJailCardMessage():
            return UseJailCardCommand(player_id=player_id)
        case ProposeTradeMessage():
            return ProposeTradeCommand(
                player_id=player_id,
                target_player_id=msg.target_player_id,
                offer_property_indices=tuple(msg.offer_property_indices),
                offer_money=msg.offer_money,
                request_property_indices=tuple(msg.request_property_indices),
                request_money=msg.request_money,
            )
        case AcceptTradeMessage():
            return AcceptTradeCommand(player_id=player_id, trade_id=msg.trade_id)
        case RejectTradeMessage():
            return RejectTradeCommand(player_id=player_id, trade_id=msg.trade_id)
        case DeclareBankruptcyMessage():
            return DeclareBankruptcyCommand(player_id=player_id)
        case _:
            raise ValueError(f"Unknown action: {type(msg).__name__}")
