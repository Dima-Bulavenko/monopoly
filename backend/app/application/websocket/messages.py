from pydantic import BaseModel
from app.application.websocket.interfaces import MessageType


class BaseMessage[PayloadT: BaseModel](BaseModel):
    type: str
    payload: PayloadT


class JoinGamePayload(BaseModel):
    game_id: str
    player_id: str


class JoinGameMessage(BaseMessage[JoinGamePayload]):
    type: MessageType = MessageType.JOIN_GAME
