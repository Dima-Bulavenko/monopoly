"""Core domain models for the Monopoly game engine."""

from __future__ import annotations

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class GameStatus(str, Enum):
    LOBBY = "lobby"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class TurnPhase(str, Enum):
    WAITING_FOR_ROLL = "waiting_for_roll"
    WAITING_FOR_BUY_DECISION = "waiting_for_buy_decision"
    IN_AUCTION = "in_auction"
    WAITING_FOR_TRADE_RESPONSE = "waiting_for_trade_response"
    IN_JAIL = "in_jail"  # player is in jail — must pay, use card, or roll
    END_OF_TURN = "end_of_turn"  # player must explicitly end their turn


class TradeStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PropertyState(BaseModel):
    square_index: int
    owner_id: str | None = None
    houses: int = 0  # 0–4
    hotel: bool = False
    mortgaged: bool = False


class AuctionState(BaseModel):
    property_index: int
    bids: dict[str, int] = Field(default_factory=dict)  # player_id → current bid
    passed_player_ids: list[str] = Field(default_factory=list)
    current_bidder_index: int = 0  # index into the active (non-passed) player list


class TradeOffer(BaseModel):
    trade_id: str
    proposer_id: str
    target_id: str
    offer_property_indices: list[int] = Field(default_factory=list)
    offer_money: int = 0
    request_property_indices: list[int] = Field(default_factory=list)
    request_money: int = 0
    status: TradeStatus = TradeStatus.PENDING


class Player(BaseModel):
    player_id: str
    name: str
    position: int = 0
    balance: int = 1500
    in_jail: bool = False
    jail_turns: int = 0
    consecutive_doubles: int = 0
    get_out_of_jail_cards: int = 0
    is_bankrupt: bool = False

    @classmethod
    def create(cls, name: str) -> "Player":
        return cls(player_id=str(uuid4()), name=name)


class Game(BaseModel):
    game_id: str
    status: GameStatus = GameStatus.LOBBY
    players: list[Player] = Field(default_factory=list)
    current_player_index: int = 0
    phase: TurnPhase = TurnPhase.WAITING_FOR_ROLL

    # {square_index: PropertyState} for all purchasable squares
    properties: dict[int, PropertyState] = Field(default_factory=dict)

    # Card deck order stored as lists of card IDs (serialisable)
    community_chest_deck: list[str] = Field(default_factory=list)
    chance_deck: list[str] = Field(default_factory=list)

    # Active sub-states
    pending_auction: AuctionState | None = None
    pending_trade: TradeOffer | None = None

    # Dice state — last roll, retained for utility rent calculation
    last_roll: tuple[int, int] = (0, 0)

    # Free Parking pot (optional house rule — engine always populates it,
    # product can choose whether to award it)
    free_parking_pot: int = 0

    # Optimistic-locking version incremented on every save
    version: int = 0

    # ----------------------------------------------------------------------
    # Convenience helpers
    # ----------------------------------------------------------------------

    @classmethod
    def create(cls) -> "Game":
        from app.domain.board.squares import (
            BOARD,
            PropertySquare,
            RailroadSquare,
            UtilitySquare,
        )

        game = cls(game_id=str(uuid4()))
        for sq in BOARD:
            if isinstance(sq, (PropertySquare, RailroadSquare, UtilitySquare)):
                game.properties[sq.index] = PropertyState(square_index=sq.index)
        return game

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    @property
    def active_players(self) -> list[Player]:
        return [p for p in self.players if not p.is_bankrupt]

    def player_by_id(self, player_id: str) -> Player:
        for p in self.players:
            if p.player_id == player_id:
                return p
        raise ValueError(f"Player {player_id} not found")
