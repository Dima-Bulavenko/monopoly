# Monopoly Project Guidelines

## Architecture

Clean Architecture — strict layer separation, no upward dependencies:

```
domain/        → Pure business logic. No I/O, no frameworks.
application/   → Use-case services and DTOs.
infrastructure → DynamoDB repos, WebSocket broadcasters.
api/           → FastAPI HTTP routers and WebSocket handlers.
```

## Backend

**Stack**: Python 3.14+, FastAPI, `mangum` (Lambda adapter), `aioboto3` (DynamoDB), `uv` (package manager).

**Code style**:
- Async/await everywhere.
- Type hints on all functions. Use PEP 604 union syntax: `str | None`, not `Optional[str]`.
- `dataclass` for domain models; `frozen=True` for events and commands.
- Pydantic only at the application layer (DTOs). Never in the domain.
- `match/case` for command dispatch in the engine.

**Domain rules**:
- `GameEngine.process(game, command, rng) → (new_game, list[Event])` is a **pure function** — no I/O, no side effects. Deep-copy before mutating.
- Inject `random.Random` (never call `random` directly) to keep logic deterministic and testable.
- New game commands → add to `domain/game/commands.py` (frozen dataclass inheriting `Command`).
- New game events → add to `domain/game/events.py` (frozen dataclass).

**Repositories**:
- `GameRepository`: `load(game_id) → Game`, `save(game) → None`. Uses optimistic locking via `version` field.
- `ConnectionRepository`: dual-key DynamoDB design — lookup by game or by connection.

**Dependency injection**: manual factory pattern (`_make_game_service()` in each router/handler). No DI container.

**Error handling**: raise domain exceptions (`InvalidActionError`, `NotYourTurnError`, etc.) from `domain/exceptions.py`. Never return error codes from the engine.

## Frontend

**Stack**: React 19, TypeScript, TanStack Start, TanStack Router (file-based), TanStack Query, Zustand, Tailwind CSS 4, Biome.

- Add routes as files under `src/routes/`. Run `routeTree.gen.ts` is auto-generated — do not edit manually.
- Server state → TanStack Query. Client-only UI state → Zustand or local `useState`.
- Use Radix UI primitives (already in `src/components/ui/`) before adding new UI libraries.
- Lint/format with Biome (`npm run lint`, `npm run format`).

## Build & Test

All commands run from the monorepo root via Make:

```sh
make up          # Start DynamoDB Local (Docker)
make db-init     # Create DynamoDB table (run once after 'make up')
make be-dev      # Backend dev server — port 8000
make fe-dev      # Frontend dev server (Vite)
make dev         # Full local stack (infra + both servers)

make be-test     # pytest
make be-lint     # ruff check
make be-format   # ruff format
make be-typecheck # ty check

make fe-lint     # biome lint
make fe-format   # biome format
```

## WebSocket Architecture

- **Local dev**: FastAPI WebSocket at `ws://localhost:8000/ws/{game_id}?player_id={player_id}`. In-memory `LocalWebSocketBroadcaster`.
- **Production**: AWS API Gateway WebSocket routes (`$connect`, `$disconnect`, default `*`). `WebSocketBroadcaster` uses `aioboto3` to push via API Gateway Management API.
- Message format: `{ "action": "roll_dice", "payload": {} }`.
- Response format: `{ "type": "game_update", "events": [...], "state": {...} }`.

## Infrastructure

- **DynamoDB single-table** design. Partition key patterns: `GAME#{game_id}`, `CONNECTION#{conn_id}`.
- Local DynamoDB runs on port 8002 (Docker). Set `DYNAMODB_ENDPOINT_URL=http://localhost:8002` in `.env`.
- Optimistic locking: always increment `version` on save; raise on version mismatch.
