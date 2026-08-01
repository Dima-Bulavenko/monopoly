from app.application.websocket.messages import JoinedGameMessage


class JoinedGameHandler:
    async def handle(self, message: JoinedGameMessage) -> None: ...
