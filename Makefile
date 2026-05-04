.PHONY: help \
        up down \
        db-init \
        be-install be-dev be-test be-test-cov be-lint be-format be-typecheck \
        fe-install fe-dev fe-build fe-lint fe-format \
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
	@echo "DynamoDB Local ready on http://localhost:8000"

down: ## Stop DynamoDB Local
	docker compose down

db-init: ## Create the DynamoDB table locally (run once after 'make up')
	cd $(BACKEND_DIR) && uv run python scripts/init_local_db.py

# ── Backend ───────────────────────────────────────────────────────────────────
be-install: ## Install backend dependencies
	cd $(BACKEND_DIR) && uv sync

be-dev: ## Run backend dev server (uvicorn + hot-reload)
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --port 8001

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

# ── Compound ──────────────────────────────────────────────────────────────────
dev: up db-init ## Start full local dev environment (infra + both servers in parallel)
	@echo "Starting backend and frontend..."
	@$(MAKE) be-dev & $(MAKE) fe-dev & wait
