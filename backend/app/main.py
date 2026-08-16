from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.routing import APIRoute
from mangum import Mangum

from app.api.http.game_router import router as game_router
from app.api.http.board_router import router as board_router
from app.auth.api.router import router as auth_router
from app.auth.infrastructure.db.postgres import get_engine
from app.bootstrap import container, register_websocket_event_handlers
from app.config import settings

_IS_LOCAL = settings.is_local

register_websocket_event_handlers(container)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    # Dispose the async Postgres engine on shutdown to close all connections.
    await get_engine().dispose()


def custom_generate_unique_id(route: APIRoute):
    return f"{route.name}"


app = FastAPI(
    title="Monopoly API",
    generate_unique_id_function=custom_generate_unique_id,
    description="API for managing a Monopoly game, including players, properties, and game state.",
    version="0.1.0",
    lifespan=_lifespan,
    # root_path is only needed when behind API Gateway
    root_path="/api/v1",
)

app.include_router(game_router)
app.include_router(auth_router)
app.include_router(board_router)

if _IS_LOCAL:
    # In local dev, WebSocket is handled by FastAPI directly (no API Gateway)
    from app.api.dev_ws import router as dev_ws_router

    app.include_router(dev_ws_router)

app.get("/", tags=["health"], include_in_schema=False)(
    lambda: {"status": "Project is running"}
)

# AWS Lambda entry point for HTTP routes (ignored when running with uvicorn locally)
lambda_handler = Mangum(app, lifespan="off")
