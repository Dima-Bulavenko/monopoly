from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from mangum import Mangum

from app.api.http.game_router import router as game_router
from app.auth.api.router import router as auth_router
from app.auth.infrastructure.db.postgres import get_engine
from app.config import settings

_IS_LOCAL = settings.is_local


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    # Dispose the async Postgres engine on shutdown to close all connections.
    await get_engine().dispose()


app = FastAPI(
    title="Monopoly API",
    description="API for managing a Monopoly game, including players, properties, and game state.",
    version="0.1.0",
    lifespan=_lifespan,
    # root_path is only needed when behind API Gateway
    root_path="" if _IS_LOCAL else "/api/v1",
)

app.include_router(game_router)
app.include_router(auth_router)

if _IS_LOCAL:
    # In local dev, WebSocket is handled by FastAPI directly (no API Gateway)
    from app.api.dev_ws import router as dev_ws_router

    app.include_router(dev_ws_router)

app.get("/", tags=["health"])(lambda: {"status": "Project is running"})

# AWS Lambda entry point for HTTP routes (ignored when running with uvicorn locally)
lambda_handler = Mangum(app, lifespan="off")
