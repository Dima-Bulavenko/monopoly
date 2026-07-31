from typing import Annotated, Literal
from pydantic import BaseModel, TypeAdapter, Field
from app.application.websocket.interfaces import (
    OutboundMessageNames,
    InboundMessagesNames,
)
from app.domain.game.models import Player


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


OutboundMessages = Annotated[
    JoinedGameMessage,
    Field(discriminator="type"),
]

outbound_messages_adapter = TypeAdapter[OutboundMessages](OutboundMessages)
