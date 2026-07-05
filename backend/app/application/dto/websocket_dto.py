"""Pydantic DTOs for WebSocket message envelopes."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from app.domain.game.events import Event
from app.application.dto.game_dto import GameStateResponse

# ---------------------------------------------------------------------------
# Inbound message classes (one per action, discriminated by `action` field)
# ---------------------------------------------------------------------------


class _InboundBase(BaseModel):
    model_config = ConfigDict(frozen=True)


class RollDiceMessage(_InboundBase):
    action: Literal["roll_dice"] = "roll_dice"


class BuyPropertyMessage(_InboundBase):
    action: Literal["buy_property"] = "buy_property"


class PassPropertyMessage(_InboundBase):
    action: Literal["pass_property"] = "pass_property"


class AuctionBidMessage(_InboundBase):
    action: Literal["auction_bid"] = "auction_bid"
    amount: int


class AuctionPassMessage(_InboundBase):
    action: Literal["auction_pass"] = "auction_pass"


class EndTurnMessage(_InboundBase):
    action: Literal["end_turn"] = "end_turn"


class BuildHouseMessage(_InboundBase):
    action: Literal["build_house"] = "build_house"
    property_index: int


class SellHouseMessage(_InboundBase):
    action: Literal["sell_house"] = "sell_house"
    property_index: int


class BuildHotelMessage(_InboundBase):
    action: Literal["build_hotel"] = "build_hotel"
    property_index: int


class SellHotelMessage(_InboundBase):
    action: Literal["sell_hotel"] = "sell_hotel"
    property_index: int


class MortgagePropertyMessage(_InboundBase):
    action: Literal["mortgage_property"] = "mortgage_property"
    property_index: int


class UnmortgagePropertyMessage(_InboundBase):
    action: Literal["unmortgage_property"] = "unmortgage_property"
    property_index: int


class PayJailFineMessage(_InboundBase):
    action: Literal["pay_jail_fine"] = "pay_jail_fine"


class UseJailCardMessage(_InboundBase):
    action: Literal["use_jail_card"] = "use_jail_card"


class ProposeTradeMessage(_InboundBase):
    action: Literal["propose_trade"] = "propose_trade"
    target_player_id: str
    offer_property_indices: list[int] = []
    offer_money: int = 0
    request_property_indices: list[int] = []
    request_money: int = 0


class AcceptTradeMessage(_InboundBase):
    action: Literal["accept_trade"] = "accept_trade"
    trade_id: str


class RejectTradeMessage(_InboundBase):
    action: Literal["reject_trade"] = "reject_trade"
    trade_id: str


class DeclareBankruptcyMessage(_InboundBase):
    action: Literal["declare_bankruptcy"] = "declare_bankruptcy"


class GetLobbyStateMessage(_InboundBase):
    """Client sends this after connecting to receive the current game/lobby state."""

    action: Literal["get_lobby_state"] = "get_lobby_state"


_InboundUnion = Annotated[
    RollDiceMessage
    | BuyPropertyMessage
    | PassPropertyMessage
    | AuctionBidMessage
    | AuctionPassMessage
    | EndTurnMessage
    | BuildHouseMessage
    | SellHouseMessage
    | BuildHotelMessage
    | SellHotelMessage
    | MortgagePropertyMessage
    | UnmortgagePropertyMessage
    | PayJailFineMessage
    | UseJailCardMessage
    | ProposeTradeMessage
    | AcceptTradeMessage
    | RejectTradeMessage
    | DeclareBankruptcyMessage
    | GetLobbyStateMessage,
    Field(discriminator="action"),
]

InboundAdapter: TypeAdapter[_InboundUnion] = TypeAdapter(_InboundUnion)

# ---------------------------------------------------------------------------
# Outbound message classes (discriminated by `type` field)
# ---------------------------------------------------------------------------


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str


class GameUpdateMessage(BaseModel):
    type: Literal["game_update"] = "game_update"
    events: list[dict[str, Any]] = []
    state: GameStateResponse | None = None


_OutboundUnion = Annotated[
    GameUpdateMessage | ErrorMessage,
    Field(discriminator="type"),
]

OutboundAdapter: TypeAdapter[_OutboundUnion] = TypeAdapter(_OutboundUnion)

# ---------------------------------------------------------------------------
# Legacy generic classes kept for compatibility
# ---------------------------------------------------------------------------


class InboundMessage(BaseModel):
    """Generic inbound message envelope."""

    action: str
    payload: dict[str, Any] = {}


class OutboundMessage(BaseModel):
    """Generic outbound message envelope."""

    type: str
    events: list[dict[str, Any]] = []
    state: dict[str, Any] | None = None
    error: str | None = None


def event_to_dto(event: Event) -> dict[str, Any]:
    """Serialise a domain event to a JSON-safe dict, adding a 'type' discriminator."""
    d = event.model_dump(mode="json")
    d["type"] = type(event).__name__
    return d
