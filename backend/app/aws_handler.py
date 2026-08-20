from typing import Any
from mangum import Mangum


def websocket_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    return {"notImplemented": "WebSocket events are not supported yet."}


def api_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    from app.main import app

    return Mangum(app, lifespan="off")(event, context)


def lambda_handler(event, context):
    if event["requestContext"].get("connectionId"):
        return websocket_handler(event, context)

    return api_handler(event, context)
