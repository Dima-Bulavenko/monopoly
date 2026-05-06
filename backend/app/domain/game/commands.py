"""Commands that players can send to the game engine."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Command(BaseModel):
    """Base class for all game commands."""

    model_config = ConfigDict(frozen=True)

    player_id: str


# ---------------------------------------------------------------------------
# Turn commands
# ---------------------------------------------------------------------------


class RollDiceCommand(Command):
    pass


class EndTurnCommand(Command):
    pass


# ---------------------------------------------------------------------------
# Property commands
# ---------------------------------------------------------------------------


class BuyPropertyCommand(Command):
    """Player chooses to buy the property they just landed on."""

    pass


class PassPropertyCommand(Command):
    """Player declines to buy — triggers an auction."""

    pass


# ---------------------------------------------------------------------------
# Auction commands
# ---------------------------------------------------------------------------


class AuctionBidCommand(Command):
    amount: int


class AuctionPassCommand(Command):
    """Player opts out of the current auction round."""

    pass


# ---------------------------------------------------------------------------
# Building commands
# ---------------------------------------------------------------------------


class BuildHouseCommand(Command):
    property_index: int


class SellHouseCommand(Command):
    property_index: int


class BuildHotelCommand(Command):
    property_index: int


class SellHotelCommand(Command):
    property_index: int


# ---------------------------------------------------------------------------
# Mortgage commands
# ---------------------------------------------------------------------------


class MortgagePropertyCommand(Command):
    property_index: int


class UnmortgagePropertyCommand(Command):
    property_index: int


# ---------------------------------------------------------------------------
# Jail commands
# ---------------------------------------------------------------------------


class PayJailFineCommand(Command):
    pass


class UseJailCardCommand(Command):
    pass


# ---------------------------------------------------------------------------
# Trade commands
# ---------------------------------------------------------------------------


class ProposeTradeCommand(Command):
    target_player_id: str
    offer_property_indices: tuple[int, ...] = ()
    offer_money: int = 0
    request_property_indices: tuple[int, ...] = ()
    request_money: int = 0


class AcceptTradeCommand(Command):
    trade_id: str


class RejectTradeCommand(Command):
    trade_id: str


# ---------------------------------------------------------------------------
# Bankruptcy
# ---------------------------------------------------------------------------


class DeclareBankruptcyCommand(Command):
    pass
