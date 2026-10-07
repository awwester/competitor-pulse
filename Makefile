.PHONY: help dev down build logs logs-worker migrate makemigrations seed \
        demo-reset demo-advance run test lint format eval shell

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n\n"} \
	     /^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ── Docker ─────────────────────────────────────────────────────────────────────

dev: demo-reset ## Start all services with hot-reload
	docker compose up --build

down: ## Stop all services
	docker compose down

build: ## Build images
	docker compose build

logs: ## Tail logs for all services
	docker compose logs -f

logs-worker: ## Tail worker (agent) logs
	docker compose logs -f worker

shell: ## Open a shell in the api container
	docker compose exec api bash

# ── Database ───────────────────────────────────────────────────────────────────

migrate: ## Apply database migrations
	docker compose exec api alembic upgrade head

makemigrations: ## Autogenerate a migration: make makemigrations m="add foo"
	docker compose exec api alembic revision --autogenerate -m "$(m)"

seed: ## Seed the demo workspace (fictional company + competitors)
	docker compose exec api python -m app.cli seed-demo

# ── Demo competitor sites ──────────────────────────────────────────────────────

# Copy into public/ rather than replacing it: nginx bind-mounts the directory itself.
demo-reset: ## Serve the "before" version of the demo competitor sites
	mkdir -p demo_sites/public && rm -rf demo_sites/public/* && cp -r demo_sites/v1/. demo_sites/public/

demo-advance: ## Serve the "after" version, so the next run finds changes
	mkdir -p demo_sites/public && rm -rf demo_sites/public/* && cp -r demo_sites/v2/. demo_sites/public/

run: ## Queue a run now
	curl -s -X POST http://localhost:8000/api/v1/runs | python3 -m json.tool

# ── Quality ────────────────────────────────────────────────────────────────────

test: ## Run backend tests (no API calls)
	docker compose exec -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/competitor_pulse_test api pytest

lint: ## Lint backend and frontend
	docker compose exec api ruff check .
	docker compose exec frontend npm run lint

format: ## Format backend code
	docker compose exec api ruff format .

eval: ## Run agent evals against the real API (costs money)
	docker compose exec -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/competitor_pulse_test worker python -m evals.run
