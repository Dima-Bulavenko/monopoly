"""Core domain models for the Monopoly game engine."""

from __future__ import annotations
from typing import Annotated

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


IdType = Annotated[str, Field(default_factory=lambda: str(uuid4()))]

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
    trade_id: IdType
    proposer_id: str
    target_id: str
    offer_property_indices: list[int] = Field(default_factory=list)
    offer_money: int = 0
    request_property_indices: list[int] = Field(default_factory=list)
    request_money: int = 0
    status: TradeStatus = TradeStatus.PENDING


class Player(BaseModel):
    player_id: IdType
    name: str
    position: int = 0
    balance: int = 1500
    in_jail: bool = False
    jail_turns: int = 0
    consecutive_doubles: int = 0
    get_out_of_jail_cards: int = 0
    is_bankrupt: bool = False


class Game(BaseModel):
    game_id: IdType
    status: GameStatus = GameStatus.LOBBY
    players: list[Player] = Field(default_factory=list)
    host_player_id: str
    current_player_index: int = 0
    max_players: int = Field(ge=2, le=6)

