from typing import Annotated, Literal
from pydantic import BaseModel, TypeAdapter, Field
from app.application.websocket.interfaces import MessageType


class BaseMessage[PayloadT: BaseModel](BaseModel):
    type: str
    payload: PayloadT


class JoinGamePayload(BaseModel):
    game_id: str
    player_id: str


class JoinGameMessage(BaseMessage[JoinGamePayload]):
    type: Literal[MessageType.JOIN_GAME]


InboundMessages = Annotated[
    JoinGameMessage,
    Field(discriminator="type"),
]

inbound_messages_adapter = TypeAdapter[InboundMessages](InboundMessages)
