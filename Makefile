.PHONY: help \
        up down \
        db-init \
        be-install be-dev be-test be-test-cov be-lint be-format be-typecheck \
        fe-install fe-dev fe-build fe-lint fe-format \
        gen-types gen-openapi check-openapi hooks \
        dev

BACKEND_DIR  := backend
FRONTEND_DIR := frontend
ENV_FILE     := .env

# Load .env if it exists (for DYNAMODB_ENDPOINT_URL etc.)
-include $(ENV_FILE)
export

# ── Colours ──────────────────────────────────────────────────────────────────
BOLD  := \033[1m
RESET := \033[0m

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BOLD)%-20s$(RESET) %s\n", $$1, $$2}'

# ── Infrastructure ────────────────────────────────────────────────────────────
up: ## Start DynamoDB Local (docker compose)
	docker compose up -d
	@echo "DynamoDB Local ready on http://localhost:8002"

down: ## Stop DynamoDB Local
	docker compose down

db-init: ## Create the DynamoDB table locally (run once after 'make up')
	cd $(BACKEND_DIR) && uv run python scripts/init_local_db.py

be-migrate: ## Apply pending Alembic migrations to local Postgres
	cd $(BACKEND_DIR) && uv run alembic upgrade head

# ── Backend ───────────────────────────────────────────────────────────────────
be-install: ## Install backend dependencies
	cd $(BACKEND_DIR) && uv sync

be-dev: ## Run backend dev server (uvicorn + hot-reload)
	cd $(BACKEND_DIR) && uv run fastapi dev

be-test: ## Run backend unit tests
	cd $(BACKEND_DIR) && uv run pytest

be-test-cov: ## Run backend tests with coverage report
	cd $(BACKEND_DIR) && uv run coverage run -m pytest && uv run coverage report -m

be-lint: ## Lint backend with ruff
	cd $(BACKEND_DIR) && uv run ruff check .

be-format: ## Format backend with ruff
	cd $(BACKEND_DIR) && uv run ruff format .

be-typecheck: ## Type-check backend with ty
	cd $(BACKEND_DIR) && uv run ty check

# ── Frontend ──────────────────────────────────────────────────────────────────
fe-install: ## Install frontend dependencies
	cd $(FRONTEND_DIR) && npm install

fe-dev: ## Run frontend dev server (Vite)
	cd $(FRONTEND_DIR) && npm run dev

fe-build: ## Build frontend for production
	cd $(FRONTEND_DIR) && npm run build

fe-lint: ## Lint frontend
	cd $(FRONTEND_DIR) && npm run lint

fe-format: ## Format frontend
	cd $(FRONTEND_DIR) && npm run format

# ── Git hooks ─────────────────────────────────────────────────────────────────
hooks: ## Install pre-commit hooks (including pre-push for schema staleness check)
	pre-commit install
	pre-commit install --hook-type pre-push

# ── Type generation ───────────────────────────────────────────────────────────
gen-types: ## Regenerate ws_schema.json and frontend/src/types/ws.ts from Pydantic DTOs
	cd $(BACKEND_DIR) && uv run python scripts/generate_ws_schema.py > ../ws_schema.json
	cd $(FRONTEND_DIR) && node scripts/gen-ws-types.mjs

gen-openapi: ## Regenerate frontend/openapi.json from the FastAPI app
	cd $(BACKEND_DIR) && uv run python scripts/generate_openapi_schema.py > ../$(FRONTEND_DIR)/openapi.json

check-openapi: ## Check that frontend/openapi.json matches the current FastAPI app
	bash $(BACKEND_DIR)/scripts/check_openapi_schema.sh

# ── Compound ──────────────────────────────────────────────────────────────────
dev: up db-init ## Start full local dev environment (infra + both servers in parallel)
	@echo "Starting backend and frontend..."
	@$(MAKE) be-dev & $(MAKE) fe-dev & wait
