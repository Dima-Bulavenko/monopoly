"""Events emitted by the game engine after processing a command.

Events are plain data — they describe *what happened* and are broadcast to all
connected clients so every player's UI can update in sync.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class Event(BaseModel):
    """Base class for all game events."""

    model_config = ConfigDict(frozen=True)


# ---------------------------------------------------------------------------
# Dice / movement
# ---------------------------------------------------------------------------


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


class PlayerMovedEvent(Event):
    player_id: str
    from_position: int
    to_position: int


class PassedGoEvent(Event):
    player_id: str
    amount_collected: int


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


class PropertyLandedEvent(Event):
    """Player landed on a purchasable property (owned or unowned)."""

    player_id: str
    square_index: int


class RentPaidEvent(Event):
    payer_id: str
    owner_id: str
    square_index: int
    amount: int


class PropertyBoughtEvent(Event):
    player_id: str
    square_index: int
    price: int


class PropertyMortgagedEvent(Event):
    player_id: str
    square_index: int
    mortgage_value: int


class PropertyUnmortgagedEvent(Event):
    player_id: str
    square_index: int
    cost: int


# ---------------------------------------------------------------------------
# Auction
# ---------------------------------------------------------------------------


class AuctionStartedEvent(Event):
    square_index: int
    starting_bidder_id: str


class AuctionBidPlacedEvent(Event):
    player_id: str
    amount: int


class AuctionPassedEvent(Event):
    player_id: str


class AuctionWonEvent(Event):
    player_id: str
    square_index: int
    amount: int


class AuctionEndedWithNoBidderEvent(Event):
    square_index: int


# ---------------------------------------------------------------------------
# Buildings
# ---------------------------------------------------------------------------


class HouseBuiltEvent(Event):
    player_id: str
    square_index: int
    cost: int


class HouseSoldEvent(Event):
    player_id: str
    square_index: int
    refund: int


class HotelBuiltEvent(Event):
    player_id: str
    square_index: int
    cost: int


class HotelSoldEvent(Event):
    player_id: str
    square_index: int
    refund: int


# ---------------------------------------------------------------------------
# Jail
# ---------------------------------------------------------------------------


class PlayerJailedEvent(Event):
    player_id: str
    reason: Literal["go_to_jail_square", "three_doubles", "card"]


class PlayerReleasedFromJailEvent(Event):
    player_id: str
    method: Literal["paid_fine", "used_card", "rolled_doubles"]


# ---------------------------------------------------------------------------
# Taxes & cards
# ---------------------------------------------------------------------------


class TaxPaidEvent(Event):
    player_id: str
    square_index: int
    amount: int


class CardDrawnEvent(Event):
    player_id: str
    deck: Literal["community_chest", "chance"]
    card_id: str
    description: str


# ---------------------------------------------------------------------------
# Trading
# ---------------------------------------------------------------------------


class TradeProposedEvent(Event):
    trade_id: str
    proposer_id: str
    target_id: str
    offer_property_indices: tuple[int, ...]
    offer_money: int
    request_property_indices: tuple[int, ...]
    request_money: int


class TradeAcceptedEvent(Event):
    trade_id: str
    proposer_id: str
    target_id: str


class TradeRejectedEvent(Event):
    trade_id: str
    proposer_id: str
    target_id: str


# ---------------------------------------------------------------------------
# Bankruptcy & game over
# ---------------------------------------------------------------------------


class BankruptcyDeclaredEvent(Event):
    player_id: str


class TurnEndedEvent(Event):
    player_id: str
    next_player_id: str


class GameStartedEvent(Event):
    game_id: str
    player_ids: tuple[str, ...]
    first_player_id: str


class GameOverEvent(Event):
    winner_id: str


# ---------------------------------------------------------------------------
# Lobby
# ---------------------------------------------------------------------------


class PlayerJoinedLobbyEvent(Event):
    game_id: str
    player_id: str
    player_name: str
    player_count: int
    max_players: int
