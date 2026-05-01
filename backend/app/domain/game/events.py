"""Events emitted by the game engine after processing a command.

Events are plain data — they describe *what happened* and are broadcast to all
connected clients so every player's UI can update in sync.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Event:
    """Base class for all game events."""


# ---------------------------------------------------------------------------
# Dice / movement
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DiceRolledEvent(Event):
    player_id: str
    die1: int
    die2: int

    @property
    def total(self) -> int:
        return self.die1 + self.die2

    @property
    def is_doubles(self) -> bool:
        return self.die1 == self.die2


@dataclass(frozen=True)
class PlayerMovedEvent(Event):
    player_id: str
    from_position: int
    to_position: int


@dataclass(frozen=True)
class PassedGoEvent(Event):
    player_id: str
    amount_collected: int


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PropertyLandedEvent(Event):
    """Player landed on a purchasable property (owned or unowned)."""

    player_id: str
    square_index: int


@dataclass(frozen=True)
class RentPaidEvent(Event):
    payer_id: str
    owner_id: str
    square_index: int
    amount: int


@dataclass(frozen=True)
class PropertyBoughtEvent(Event):
    player_id: str
    square_index: int
    price: int


@dataclass(frozen=True)
class PropertyMortgagedEvent(Event):
    player_id: str
    square_index: int
    mortgage_value: int


@dataclass(frozen=True)
class PropertyUnmortgagedEvent(Event):
    player_id: str
    square_index: int
    cost: int


# ---------------------------------------------------------------------------
# Auction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuctionStartedEvent(Event):
    square_index: int
    starting_bidder_id: str


@dataclass(frozen=True)
class AuctionBidPlacedEvent(Event):
    player_id: str
    amount: int


@dataclass(frozen=True)
class AuctionPassedEvent(Event):
    player_id: str


@dataclass(frozen=True)
class AuctionWonEvent(Event):
    player_id: str
    square_index: int
    amount: int


@dataclass(frozen=True)
class AuctionEndedWithNoBidderEvent(Event):
    square_index: int


# ---------------------------------------------------------------------------
# Buildings
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HouseBuiltEvent(Event):
    player_id: str
    square_index: int
    cost: int


@dataclass(frozen=True)
class HouseSoldEvent(Event):
    player_id: str
    square_index: int
    refund: int


@dataclass(frozen=True)
class HotelBuiltEvent(Event):
    player_id: str
    square_index: int
    cost: int


@dataclass(frozen=True)
class HotelSoldEvent(Event):
    player_id: str
    square_index: int
    refund: int


# ---------------------------------------------------------------------------
# Jail
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlayerJailedEvent(Event):
    player_id: str
    reason: Literal["go_to_jail_square", "three_doubles", "card"]


@dataclass(frozen=True)
class PlayerReleasedFromJailEvent(Event):
    player_id: str
    method: Literal["paid_fine", "used_card", "rolled_doubles"]


# ---------------------------------------------------------------------------
# Taxes & cards
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TaxPaidEvent(Event):
    player_id: str
    square_index: int
    amount: int


@dataclass(frozen=True)
class CardDrawnEvent(Event):
    player_id: str
    deck: Literal["community_chest", "chance"]
    card_id: str
    description: str


# ---------------------------------------------------------------------------
# Trading
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TradeProposedEvent(Event):
    trade_id: str
    proposer_id: str
    target_id: str
    offer_property_indices: tuple[int, ...]
    offer_money: int
    request_property_indices: tuple[int, ...]
    request_money: int


@dataclass(frozen=True)
class TradeAcceptedEvent(Event):
    trade_id: str
    proposer_id: str
    target_id: str


@dataclass(frozen=True)
class TradeRejectedEvent(Event):
    trade_id: str
    proposer_id: str
    target_id: str


# ---------------------------------------------------------------------------
# Bankruptcy & game over
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BankruptcyDeclaredEvent(Event):
    player_id: str


@dataclass(frozen=True)
class TurnEndedEvent(Event):
    player_id: str
    next_player_id: str


@dataclass(frozen=True)
class GameStartedEvent(Event):
    game_id: str
    player_ids: tuple[str, ...]
    first_player_id: str


@dataclass(frozen=True)
class GameOverEvent(Event):
    winner_id: str
