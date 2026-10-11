# Competitor Pulse

AI agent that monitors competitor web pages, works out which changes matter to your business, and sends an approved digest to Slack/email. Setup is automated: from the company website, discovery agents draft the profile, suggest competitors (human-approved) and pick each competitor's pages.

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
# open localhost:5173 and click "Try the sample company" (or `make seed` to skip discovery)
make run               # queue a run now (first run = baseline)
make demo-advance      # switch demo sites to "after" versions, then `make run` again
make dev name=fresh    # separate instance with its own database; pass name= to any target
make destroy name=fresh  # stop that instance and delete its data
make instances         # list instances and whether they are running
```

Only one instance can run at a time (they share ports); the demo sites are shared too.

Services: api (localhost:8000, docs at /docs, MCP at /mcp), frontend (localhost:5173), demo-sites (localhost:8080), mailpit (localhost:8025), postgres (5432)

## Project Structure

- `backend/app/models/` — SQLAlchemy models. Every table hangs off `workspaces` (one per company; no accounts yet)
- `backend/app/schemas/` — Pydantic API schemas; subclass `Schema` for camelCase JSON
- `backend/app/api/` — FastAPI routers (`/api/v1`); `deps.py` has `CurrentWorkspace` (from the `/workspaces/{workspace_id}` prefix), `Session`, `Writable`
- `backend/app/services/` — Crawler, diffing, run queue, run event log, notifier, check schedule, URL normalization
- `backend/app/agent/` — `runner.py` (shared options + query loop), `tool_results.py`, `tracing.py` (SDK messages → trace events); one package per agent with `prompts.py` + `tools.py` (MCP tools bound to one run): `analyst/`, `discovery/`
- `backend/app/mcp_server/` — MCP server for outside agents, mounted at `/mcp`; tools call the same services as the REST API (no publish/approval tools)
- `backend/app/worker/` — Worker entrypoint; `pipeline.py` dispatches a run by `RunKind`: `check.py` (crawl → diff → analyst → awaiting review), `discovery.py` (company discovery → awaiting review → apply; page discovery → completed)
- `backend/evals/` — Agent evals against the real API (`make eval`); analyst cases in `evals/cases/*.json`, discovery cases in `evals/run.py` (need `demo-sites`)
- `backend/tests/` — pytest suite; never calls the Claude API
- `frontend/src/{pages,components/<domain>,hooks,lib,types}` — components organized by domain
- `demo_sites/v1|v2` — Fictional company (Tallybird) and competitor pages served by nginx for local demos; keep v1/v2 identical except for the intended changes

## Conventions

- UUID primary keys and timestamptz `created_at`/`updated_at` via `BaseEntity`
- Enums are `StrEnum` stored as varchar via `str_enum()`
- Generate migrations with `make makemigrations m="..."`; never hand-write them
- Services raise `NotFound`/`Conflict`/`ReadOnly` (`services/errors.py`); `main.py` maps them to HTTP statuses and `mcp_server` to tool errors, so routers and MCP tools stay thin
- Agent tools return `{"content": [...]}` and signal bad input with `"is_error": True` rather than raising
- Frontend path alias `@/` → `src/`; mutations go through `useApiMutation` (invalidate + toast)

## Testing

- `make test` runs pytest inside Docker against the `competitor_pulse_test` database
- Tests use helpers in `tests/factories.py`; fake the crawler/agent with `monkeypatch`, never real API calls
- One behavior per test; name describes the behavior
- `make eval` runs the agent on fixed before/after cases (costs money)
