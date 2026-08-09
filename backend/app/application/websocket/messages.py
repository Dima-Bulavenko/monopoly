from typing import Annotated, Literal
from pydantic import BaseModel, TypeAdapter, Field
from app.application.websocket.interfaces import (
    OutboundMessageNames,
    InboundMessagesNames,
)
from app.domain.game.models import Player, GameStatus


class BaseMessage[PayloadT: BaseModel](BaseModel):
    type: str
    payload: PayloadT


class InboundMessage(BaseMessage[BaseModel]):
    type: InboundMessagesNames


inbound_messages_adapter = TypeAdapter[InboundMessage](InboundMessage)

# Outbound messages


class JoinedGamePayload(BaseModel):
    game_id: str
    player: Player


class JoinedGameMessage(BaseMessage[JoinedGamePayload]):
    type: Literal[OutboundMessageNames.JOINED_GAME] = OutboundMessageNames.JOINED_GAME


class GameStartedPayload(BaseModel):
    game_id: str
    status: Literal[GameStatus.IN_PROGRESS] = GameStatus.IN_PROGRESS


class GameStartedMessage(BaseMessage[GameStartedPayload]):
    type: Literal[OutboundMessageNames.GAME_STARTED] = OutboundMessageNames.GAME_STARTED


OutboundMessages = Annotated[
    JoinedGameMessage,
    GameStartedMessage,
    Field(discriminator="type"),
]

outbound_messages_adapter = TypeAdapter[OutboundMessages](OutboundMessages)
