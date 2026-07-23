from typing import Protocol
from enum import StrEnum


class MessageType(StrEnum):
    JOIN_GAME = "join_game"


class IMessage(Protocol):
    type: MessageType


class IMessageHandler(Protocol):
    async def handle(self, message: IMessage) -> None: ...
