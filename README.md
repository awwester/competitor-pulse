# Competitor Pulse

**A self-hosted AI analyst that watches your competitors' websites and tells you what changed and why it matters to *your* business.**

Every week (or whenever you click *Run check now*), Competitor Pulse re-reads the pricing pages, changelogs, homepages and careers pages you track. When something changes, an agent built on the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) reads the diffs, checks what it has already reported, scores each change against your company profile, and writes a brief. You review it, dismiss anything off-base, and approve. Only then does it go to Slack or email.

> "Ledgerly cut Pro to $29 and added automatic payment reminders, our main differentiator. Consider leading the next campaign with multi-currency, which they still lack."

![Run detail: findings, analyst report and the live agent trace](docs/run-detail.png)

## Why it's built this way

Most "AI agent" demos are a chat box. This one shows the patterns real agentic products need:

| Concern | How it's handled |
|---|---|
| **Don't spend tokens on nothing** | A deterministic crawl and diff runs first. The LLM is only called when visible page text actually changed, and the first capture of a page is a free baseline. |
| **Give the agent tools, not a prompt dump** | Six in-process MCP tools (`list_changed_pages`, `get_page_diff`, `get_page_content`, `get_recent_findings`, `record_finding`, `submit_report`) plus `WebSearch`/`WebFetch` for outside context. All other Claude Code tools are disabled. |
| **Scope and safety** | Tools are bound to a single run, so the agent can only read and write that run's data. `permission_mode="dontAsk"` denies anything not allow-listed, `setting_sources=[]` isolates it from host config, and the agent runs in a throwaway working directory. |
| **Memory across runs** | `get_recent_findings` lets the agent see what it already reported for a competitor, so it doesn't repeat itself week after week. |
| **Observability** | Every model message, tool call and tool result is saved as a trace event and streamed to the UI live. Tokens, cache hits, turns and cost are recorded per run. |
| **Cost guardrails** | Per-run `max_budget_usd` and `max_turns`, a configurable model and effort level, and spend shown on every run and the dashboard. |
| **Human in the loop** | Runs end in `awaiting_review`. Nothing leaves the system until someone approves, and individual findings can be dismissed first. |
| **Evals, not vibes** | `make eval` runs the real agent on fixed before/after cases (a price cut, pure noise, a repositioning, a hiring push, routine bug fixes) and checks categories and significance. |
| **No extra infrastructure** | The Postgres `runs` table is the job queue (`SELECT … FOR UPDATE SKIP LOCKED`), so there's no Redis or broker, and more workers can be added safely. |

## Architecture

```
            ┌──────────────┐  cron / "Run now"   ┌────────────────────────────────────────┐
 React UI ─▶│  FastAPI     │── insert run ──────▶│ Postgres (runs = queue, snapshots,     │
  (live     │  /api/v1     │◀── trace, findings ─│  findings, run_events)                 │
  trace)    └──────────────┘                     └───────────────┬────────────────────────┘
                                                                 │ claim (SKIP LOCKED)
                                                       ┌─────────▼─────────┐
                                                       │      Worker       │
                                                       │ 1. Playwright     │──▶ competitor sites
                                                       │ 2. normalize+diff │
                                                       │ 3. Claude Agent   │──▶ Claude API
                                                       │    SDK + MCP tools│    (+ web search)
                                                       └─────────┬─────────┘
                                                                 ▼
                                               awaiting_review ──approve──▶ Slack / email
```

## Quick start

Requirements: Docker and an [Anthropic API key](https://console.anthropic.com/).

```bash
git clone https://github.com/awwester/competitor-pulse.git
cd competitor-pulse
cp .env.example .env          # add ANTHROPIC_API_KEY
make dev                      # api, worker, frontend, postgres, demo sites, mailpit
```

In a second terminal, try the built-in demo. It uses fictional competitors served locally, so no real sites are touched:

```bash
make seed           # demo company "Tallybird" + two fictional competitors
make run            # first run captures a baseline of each page (no LLM call)
make demo-advance   # competitors "update" their sites
make run            # the agent analyzes the changes
```

Open http://localhost:5173 and watch the trace stream in. Approve the report, and the digest shows up in Mailpit at http://localhost:8025.

To track real competitors, open **Settings**, describe your company (the agent judges every change against this), then add competitors and their pages.

## Configuration

| Variable | Default | |
|---|---|---|
| `ANTHROPIC_API_KEY` | | Required by the worker |
| `AGENT_MODEL` | `claude-opus-5-5` | Any Claude model ID |
| `AGENT_EFFORT` | `medium` | `low` … `max` |
| `AGENT_MAX_BUDGET_USD` | `2.0` | Hard stop per run |
| `SCHEDULE_CRON` | `0 8 * * MON` | When scheduled runs fire (worker timezone) |
| `DEMO_MODE` | `false` | Read-only API for a public demo deployment |

Slack webhook and email recipients are set in the UI under **Settings**.

## Development

```bash
make test       # backend tests (no API calls)
make lint       # ruff + eslint
make eval       # agent evals against the real API, roughly $1
make help       # everything else
```

Project layout and conventions are in [CLAUDE.md](CLAUDE.md).

## Roadmap

- Auth and multi-workspace (the schema is already workspace-scoped)
- Screenshot diffs alongside text diffs
- RSS / sitemap discovery of new pages
- Hosted read-only demo

## License

MIT
