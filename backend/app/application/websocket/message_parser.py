from app.application.websocket.messages import BaseMessage


class MessageParser:
    def __init__(self, registry) -> None:
        self.registry = registry

    def parse(self, data: dict) -> BaseMessage:
        message_type = data.get("type")

        schema = self.registry.get(message_type)

        if schema is None:
            raise ValueError(f"Unknown message type: {message_type}")

        return schema.model_validate(data)
