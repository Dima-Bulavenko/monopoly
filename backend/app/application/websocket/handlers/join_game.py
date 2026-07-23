from app.application.websocket.messages import JoinGameMessage


class JoinGameHandler:
    def __init__(
        self,
        game_service,
    ):
        self.game_service = game_service

    async def handle(
        self,
        message: JoinGameMessage,
    ):
        user_id = message.payload.player_id
        await self.game_service.join_game(
            user_id=user_id,
            game_id=message.payload.game_id,
        )
