from fastapi import FastAPI


app = FastAPI(
    title="Monopoly API",
    description="API for managing a Monopoly game, including players, properties, and game state.",
    version="0.1.0",
    root_path="/api/v1",
)


app.get("/", tags=["health"])(lambda: {"status": "Project is running"})
