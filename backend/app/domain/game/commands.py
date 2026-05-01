"""Commands that players can send to the game engine."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Command:
    """Base class for all game commands."""

    player_id: str


# ---------------------------------------------------------------------------
# Turn commands
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RollDiceCommand(Command):
    pass


@dataclass(frozen=True)
class EndTurnCommand(Command):
    pass


# ---------------------------------------------------------------------------
# Property commands
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BuyPropertyCommand(Command):
    """Player chooses to buy the property they just landed on."""

    pass


@dataclass(frozen=True)
class PassPropertyCommand(Command):
    """Player declines to buy — triggers an auction."""

    pass


# ---------------------------------------------------------------------------
# Auction commands
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuctionBidCommand(Command):
    amount: int


@dataclass(frozen=True)
class AuctionPassCommand(Command):
    """Player opts out of the current auction round."""

    pass


# ---------------------------------------------------------------------------
# Building commands
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BuildHouseCommand(Command):
    property_index: int


@dataclass(frozen=True)
class SellHouseCommand(Command):
    property_index: int


@dataclass(frozen=True)
class BuildHotelCommand(Command):
    property_index: int


@dataclass(frozen=True)
class SellHotelCommand(Command):
    property_index: int


# ---------------------------------------------------------------------------
# Mortgage commands
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MortgagePropertyCommand(Command):
    property_index: int


@dataclass(frozen=True)
class UnmortgagePropertyCommand(Command):
    property_index: int


# ---------------------------------------------------------------------------
# Jail commands
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PayJailFineCommand(Command):
    pass


@dataclass(frozen=True)
class UseJailCardCommand(Command):
    pass


# ---------------------------------------------------------------------------
# Trade commands
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProposeTradeCommand(Command):
    target_player_id: str
    offer_property_indices: tuple[int, ...] = field(default_factory=tuple)
    offer_money: int = 0
    request_property_indices: tuple[int, ...] = field(default_factory=tuple)
    request_money: int = 0


@dataclass(frozen=True)
class AcceptTradeCommand(Command):
    trade_id: str


@dataclass(frozen=True)
class RejectTradeCommand(Command):
    trade_id: str


# ---------------------------------------------------------------------------
# Bankruptcy
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DeclareBankruptcyCommand(Command):
    pass
