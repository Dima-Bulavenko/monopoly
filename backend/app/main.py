from fastapi import FastAPI
from mangum import Mangum

from app.api.http.game_router import router as game_router

app = FastAPI(
    title="Monopoly API",
    description="API for managing a Monopoly game, including players, properties, and game state.",
    version="0.1.0",
    root_path="/api/v1",
)

app.include_router(game_router)

app.get("/", tags=["health"])(lambda: {"status": "Project is running"})

# AWS Lambda entry point for HTTP routes
lambda_handler = Mangum(app, lifespan="off")
