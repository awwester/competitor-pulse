"""In-process MCP tools the analyst agent uses to read this run's changes and record its output.

Every tool is bound to one run, so the agent can only see and write data for the run it is
analyzing.
"""

import json
import uuid
from typing import Any

from claude_agent_sdk import SdkMcpTool, create_sdk_mcp_server, tool
from claude_agent_sdk.types import McpSdkServerConfig
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.db import SessionLocal
from app.models import Finding, FindingCategory, Run, Snapshot, TrackedPage
from app.services.diffing import diff_text, truncate

SERVER_NAME = "pulse"
MAX_DIFF_CHARS = 15_000
MAX_PAGE_CHARS = 20_000

ToolResult = dict[str, Any]


def _text(value: str | dict | list) -> ToolResult:
    text = value if isinstance(value, str) else json.dumps(value, indent=2, default=str)
    return {"content": [{"type": "text", "text": text}]}


def _error(message: str) -> ToolResult:
    return {"content": [{"type": "text", "text": message}], "is_error": True}


def _parse_uuid(value: Any) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


FINDING_SCHEMA = {
    "type": "object",
    "properties": {
        "tracked_page_id": {"type": "string", "description": "ID from list_changed_pages."},
        "category": {"type": "string", "enum": [c.value for c in FindingCategory]},
        "significance": {"type": "integer", "minimum": 1, "maximum": 5},
        "title": {"type": "string", "description": "One line, under 100 characters."},
        "summary": {
            "type": "string",
            "description": "2-4 sentences: what changed and why it matters to us.",
        },
        "evidence": {"type": "string", "description": "Short verbatim quote(s) from the diff."},
        "recommended_action": {"type": "string", "description": "Optional. May be empty."},
    },
    "required": ["tracked_page_id", "category", "significance", "title", "summary", "evidence"],
}

REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {
            "type": "string",
            "description": (
                "The single most important takeaway, in one sentence of at most 20 words."
            ),
        },
        "report_markdown": {
            "type": "string",
            "description": "Markdown brief: key takeaways first, then per-competitor notes.",
        },
    },
    "required": ["headline", "report_markdown"],
}


def build_tools(run_id: uuid.UUID) -> list[SdkMcpTool[Any]]:
    async def changed_snapshot(
        session, tracked_page_id: uuid.UUID
    ) -> tuple[Snapshot, Snapshot] | None:
        previous = aliased(Snapshot)
        row = (
            await session.execute(
                select(Snapshot, previous)
                .join(previous, Snapshot.previous_id == previous.id)
                .where(Snapshot.run_id == run_id, Snapshot.tracked_page_id == tracked_page_id)
            )
        ).first()
        return (row[0], row[1]) if row else None

    @tool(
        "list_changed_pages",
        "List the tracked competitor pages whose content changed in this run.",
        {},
    )
    async def list_changed_pages(args: dict[str, Any]) -> ToolResult:
        previous = aliased(Snapshot)
        async with SessionLocal() as session:
            rows = (
                await session.execute(
                    select(Snapshot, previous, TrackedPage)
                    .join(previous, Snapshot.previous_id == previous.id)
                    .join(TrackedPage, Snapshot.tracked_page_id == TrackedPage.id)
                    .where(Snapshot.run_id == run_id)
                    .order_by(TrackedPage.competitor_id)
                )
            ).all()
        pages = []
        for current, before, page in rows:
            diff = diff_text(before.content, current.content)
            pages.append(
                {
                    "tracked_page_id": str(page.id),
                    "competitor_id": str(page.competitor_id),
                    "competitor": page.competitor.name,
                    "url": page.url,
                    "page_type": page.page_type,
                    "lines_added": diff.lines_added,
                    "lines_removed": diff.lines_removed,
                }
            )
        return _text(pages)

    @tool(
        "get_page_diff",
        "Get the unified diff between the previous and current text of a changed page.",
        {"tracked_page_id": str},
    )
    async def get_page_diff(args: dict[str, Any]) -> ToolResult:
        page_id = _parse_uuid(args.get("tracked_page_id"))
        async with SessionLocal() as session:
            pair = page_id and await changed_snapshot(session, page_id)
        if not pair:
            return _error("No change recorded for that tracked_page_id in this run.")
        current, before = pair
        return _text(truncate(diff_text(before.content, current.content).text, MAX_DIFF_CHARS))

    @tool(
        "get_page_content",
        "Get the full current text of a changed page, for context the diff doesn't show.",
        {"tracked_page_id": str},
    )
    async def get_page_content(args: dict[str, Any]) -> ToolResult:
        page_id = _parse_uuid(args.get("tracked_page_id"))
        async with SessionLocal() as session:
            pair = page_id and await changed_snapshot(session, page_id)
        if not pair:
            return _error("No change recorded for that tracked_page_id in this run.")
        return _text(truncate(pair[0].content, MAX_PAGE_CHARS))

    @tool(
        "get_recent_findings",
        "Get the most recent findings already reported for a competitor in earlier runs.",
        {"competitor_id": str},
    )
    async def get_recent_findings(args: dict[str, Any]) -> ToolResult:
        competitor_id = _parse_uuid(args.get("competitor_id"))
        if not competitor_id:
            return _error("competitor_id must be a UUID from list_changed_pages.")
        async with SessionLocal() as session:
            findings = (
                await session.scalars(
                    select(Finding)
                    .where(Finding.competitor_id == competitor_id, Finding.run_id != run_id)
                    .order_by(Finding.created_at.desc())
                    .limit(15)
                )
            ).all()
        return _text(
            [
                {
                    "date": f.created_at.date().isoformat(),
                    "category": f.category,
                    "significance": f.significance,
                    "title": f.title,
                }
                for f in findings
            ]
            or "No earlier findings for this competitor."
        )

    @tool("record_finding", "Record one meaningful competitor change.", FINDING_SCHEMA)
    async def record_finding(args: dict[str, Any]) -> ToolResult:
        page_id = _parse_uuid(args.get("tracked_page_id"))
        try:
            category = FindingCategory(args.get("category"))
            significance = int(args["significance"])
        except KeyError, TypeError, ValueError:
            return _error("category must be a listed value and significance an integer 1-5.")
        if not 1 <= significance <= 5:
            return _error("significance must be between 1 and 5.")
        async with SessionLocal() as session:
            if not page_id or not await changed_snapshot(session, page_id):
                return _error("tracked_page_id must be one of the pages changed in this run.")
            page = await session.get(TrackedPage, page_id)
            finding = Finding(
                run_id=run_id,
                competitor_id=page.competitor_id,
                tracked_page_id=page_id,
                category=category,
                significance=significance,
                title=str(args.get("title", ""))[:300],
                summary=str(args.get("summary", "")),
                evidence=str(args.get("evidence", "")),
                recommended_action=str(args.get("recommended_action") or ""),
            )
            session.add(finding)
            await session.commit()
        return _text(f"Recorded finding {finding.id}.")

    @tool(
        "submit_report", "Submit the final report for this run. Call exactly once.", REPORT_SCHEMA
    )
    async def submit_report(args: dict[str, Any]) -> ToolResult:
        headline = str(args.get("headline", "")).strip()
        report = str(args.get("report_markdown", "")).strip()
        if not headline or not report:
            return _error("headline and report_markdown are both required.")
        async with SessionLocal() as session:
            run = await session.get(Run, run_id)
            run.headline = headline[:500]
            run.report_markdown = report
            await session.commit()
        return _text("Report saved. You're done.")

    return [
        list_changed_pages,
        get_page_diff,
        get_page_content,
        get_recent_findings,
        record_finding,
        submit_report,
    ]


def build_server(run_id: uuid.UUID) -> tuple[McpSdkServerConfig, list[str]]:
    """Returns the MCP server config and the fully qualified tool names to allow."""
    tools = build_tools(run_id)
    server = create_sdk_mcp_server(name=SERVER_NAME, tools=tools)
    return server, [f"mcp__{SERVER_NAME}__{t.name}" for t in tools]
