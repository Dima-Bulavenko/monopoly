import os

from fastapi import FastAPI
from mangum import Mangum

from app.api.http.game_router import router as game_router

_IS_LOCAL = os.environ.get("ENV", "local") == "local"

app = FastAPI(
    title="Monopoly API",
    description="API for managing a Monopoly game, including players, properties, and game state.",
    version="0.1.0",
    # root_path is only needed when behind API Gateway
    root_path="" if _IS_LOCAL else "/api/v1",
)

app.include_router(game_router)

if _IS_LOCAL:
    # In local dev, WebSocket is handled by FastAPI directly (no API Gateway)
    from app.api.dev_ws import router as dev_ws_router

    app.include_router(dev_ws_router)

app.get("/", tags=["health"])(lambda: {"status": "Project is running"})

# AWS Lambda entry point for HTTP routes (ignored when running with uvicorn locally)
lambda_handler = Mangum(app, lifespan="off")
