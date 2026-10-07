# Competitor Pulse

Self-hosted AI agent that monitors competitor web pages, works out which changes matter to your business, and sends an approved digest to Slack/email.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy 2 (async, asyncpg), Alembic, Pydantic v2, uv
- **Agent:** Claude Agent SDK (`claude-agent-sdk`) with in-process MCP tools
- **Crawler:** Playwright (headless Chromium)
- **Worker:** Plain asyncio process; the `runs` table is the queue (`FOR UPDATE SKIP LOCKED`), APScheduler for the cron trigger
- **Frontend:** React + Vite (TypeScript), Tailwind CSS v4, TanStack Query, React Router
- **Database:** PostgreSQL

## Development

```bash
cp .env.example .env   # add ANTHROPIC_API_KEY
make dev               # all services with hot-reload
make seed              # fictional demo company + competitors
make run               # queue a run now (first run = baseline)
make demo-advance      # switch demo sites to "after" versions, then `make run` again
```

Services: api (localhost:8000, docs at /docs), frontend (localhost:5173), demo-sites (localhost:8080), mailpit (localhost:8025), postgres (5432)

## Project Structure

- `backend/app/models/` — SQLAlchemy models. Every table hangs off `workspaces` (single-tenant today, multi-tenant ready)
- `backend/app/schemas/` — Pydantic API schemas; subclass `Schema` for camelCase JSON
- `backend/app/api/` — FastAPI routers (`/api/v1`); `deps.py` has `CurrentWorkspace`, `Session`, `Writable`
- `backend/app/services/` — Crawler, diffing, run queue, run event log, notifier
- `backend/app/agent/` — Analyst agent: `prompts.py`, `tools.py` (MCP tools bound to one run), `tracing.py` (SDK messages → trace events), `analyst.py` (options + query loop)
- `backend/app/worker/` — Worker entrypoint and the run pipeline (crawl → diff → agent → awaiting review)
- `backend/evals/` — Agent evals against the real API (`make eval`); cases in `evals/cases/*.json`
- `backend/tests/` — pytest suite; never calls the Claude API
- `frontend/src/{pages,components/<domain>,hooks,lib,types}` — components organized by domain
- `demo_sites/v1|v2` — Fictional competitor pages served by nginx for local demos

## Conventions

- UUID primary keys and timestamptz `created_at`/`updated_at` via `BaseEntity`
- Enums are `StrEnum` stored as varchar via `str_enum()`
- Generate migrations with `make makemigrations m="..."`; never hand-write them
- Agent tools return `{"content": [...]}` and signal bad input with `"is_error": True` rather than raising
- Frontend path alias `@/` → `src/`; mutations go through `useApiMutation` (invalidate + toast)

## Testing

- `make test` runs pytest inside Docker against the `competitor_pulse_test` database
- Tests use helpers in `tests/factories.py`; fake the crawler/agent with `monkeypatch`, never real API calls
- One behavior per test; name describes the behavior
- `make eval` runs the agent on fixed before/after cases (costs money)
