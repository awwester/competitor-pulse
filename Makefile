.PHONY: help dev down destroy build logs logs-worker migrate makemigrations seed \
        demo-reset demo-advance run test lint format eval shell instances

# Separate instances, each with its own database: pass name=<instance> to any target,
# e.g. `make dev name=fresh`. Without it, targets use the default instance (competitor-pulse).
ifdef name
export COMPOSE_PROJECT_NAME := $(name)
endif

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n\n"} \
	     /^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ── Docker ─────────────────────────────────────────────────────────────────────

dev: demo-reset ## Start all services with hot-reload (name=<instance> creates or reuses one)
	docker compose up --build

# `stop` rather than `down`: keeping the containers keeps the instance in `make instances`.
down: ## Stop all services, keeping the data
	docker compose stop

destroy: ## Stop an instance and delete its data: make destroy name=<instance>
	@test -n "$(name)" || { echo "Name the instance to delete: make destroy name=<instance>"; exit 1; }
	docker compose down -v

instances: ## List local instances and their status
	@docker compose ls -a | awk -v file="$(CURDIR)/docker-compose.yml" \
	    'NR == 1 || index($$3, file) { printf "%-20s %s\n", $$1, $$2 }'

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

seed: ## Add the sample Tallybird company and its competitors, without running discovery
	docker compose exec api python -m app.cli seed-demo

# ── Demo competitor sites ──────────────────────────────────────────────────────

# Copy into public/ rather than replacing it: nginx bind-mounts the directory itself.
demo-reset: ## Serve the "before" version of the demo competitor sites
	mkdir -p demo_sites/public && rm -rf demo_sites/public/* && cp -r demo_sites/v1/. demo_sites/public/

demo-advance: ## Serve the "after" version, so the next run finds changes
	mkdir -p demo_sites/public && rm -rf demo_sites/public/* && cp -r demo_sites/v2/. demo_sites/public/

run: ## Queue a check for every company now
	docker compose exec api python -m app.cli run-checks

# ── Quality ────────────────────────────────────────────────────────────────────

test: ## Run backend tests (no API calls)
	docker compose exec -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/competitor_pulse_test api pytest

lint: ## Lint backend and frontend
	docker compose exec api ruff check .
	docker compose exec frontend npm run lint

format: ## Format backend code
	docker compose exec api ruff format .

eval: ## Run agent evals against the real API (costs money); pick some with cases="a b", run every agent on one model with model=...
	docker compose exec -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/competitor_pulse_test \
		$(if $(model),-e ANALYST_MODEL=$(model) -e COMPANY_DISCOVERY_MODEL=$(model) -e PAGE_DISCOVERY_MODEL=$(model)) \
		worker python -m evals.run $(cases)
