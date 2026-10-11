# MCP Server

Competitor Pulse runs agents of its own, and it is also a tool for other agents. The API serves a [Model Context Protocol](https://modelcontextprotocol.io) server at `/mcp`, so Claude Code, Claude Desktop or any MCP client can ask what competitors changed and manage the watchlist.

```
> What did our competitors change on pricing this month?

  ⏺ competitor-pulse - list_workspaces()
  ⏺ competitor-pulse - search_findings(category: "pricing", since: "2026-09-11")

  Ledgerly cut Pro to $29 and added automatic payment reminders …
```

## Connect

With `make dev` running, open Claude Code in this repo. The checked-in [`.mcp.json`](../.mcp.json) offers the server, so approve it when asked. From anywhere else:

```bash
claude mcp add --transport http competitor-pulse http://localhost:8000/mcp
```

It uses the Streamable HTTP transport, stateless, so the API can scale out like any other endpoint.

## Tools

| Tool | Does |
| --- | --- |
| `list_workspaces` | The companies being monitored, with their profiles. Call it first: every other tool takes a `workspace_id`. |
| `list_competitors` | Tracked competitors and the pages watched on each |
| `search_findings` | Past findings, filtered by competitor, category, minimum significance, date and dismissed state; most significant first |
| `list_runs` / `get_run` | Recent checks and discoveries; one run's report and findings |
| `queue_check` | Crawl now; the analyst reviews any changes and the report waits for approval |
| `add_competitor` | Track a competitor. Without pages, the page discovery agent picks them |
| `remove_competitor`, `add_page`, `remove_page` | Edit the watchlist |
| `set_finding_dismissed` | Dismiss a finding as off-base, or restore it |

Read tools are annotated `readOnlyHint` and deletions `destructiveHint`, so clients can decide which calls need a person's confirmation.

Some prompts to try:

- *Summarize the most significant competitor changes from the last check.*
- *Has anyone changed their hiring page recently? What does it suggest about their roadmap?*
- *Start tracking https://example.com as a competitor and let discovery pick its pages.*

## Security model

An MCP server hands this system's data to someone else's agent, which may also hold other tools. The design keeps that safe:

- **Publishing stays human.** Sending a digest to Slack or email, approving discovered competitors and dismissing a run's report are not exposed. An outside agent can queue a check, but the report still waits for a person in the UI. ([tool list test](../backend/tests/test_mcp_tools.py))
- **Competitor text is labelled as untrusted.** Findings, evidence and reports are derived from competitor websites, so the server's instructions and the tool descriptions tell the client agent to treat them as data, not instructions. This matters more here than inside Competitor Pulse, because the client agent might also have a shell or email. See the [agents' security model](agents.md#security-model).
- **Same rules as the UI.** Tools call the same services as the REST API, so workspace scoping (a run from another company is "not found"), the one-active-check rule and `DEMO_MODE` read-only all apply unchanged.
- **Local only, for now.** Like the rest of the API there is no login. The server accepts only `localhost` Host and Origin headers (DNS rebinding protection), so a web page can't drive it through your browser. Exposing it beyond your machine would need OAuth, which the MCP SDK supports.

## Code

- [`server.py`](../backend/app/mcp_server/server.py): server instructions, and the per-call session that turns service errors into tool errors
- [`tools.py`](../backend/app/mcp_server/tools.py): the tools, which return the API's own Pydantic schemas as structured output
- [`main.py`](../backend/app/main.py): mounted on the FastAPI app; service errors map to HTTP statuses there
