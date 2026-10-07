"""In-process MCP tools for the discovery agents.

Company discovery proposes competitors for human approval; page discovery adds pages (and
notes, when there are none) directly.
Both validate every URL by actually loading it, so a hallucinated or dead link is rejected
before anyone sees it.
"""

import uuid
from typing import Any

from claude_agent_sdk import SdkMcpTool, tool
from playwright.async_api import Error as PlaywrightError
from sqlalchemy import func, select

from app.agent.discovery.prompts import COMPETITOR_NOTES
from app.agent.tool_results import ToolResult, error, text
from app.config import settings
from app.db import SessionLocal
from app.models import (
    DEFAULT_WORKSPACE_NAME,
    Competitor,
    CompetitorSuggestion,
    PageType,
    Run,
    TrackedPage,
    Workspace,
)
from app.services.crawler import Crawler
from app.services.diffing import truncate
from app.services.urls import same_host, site_key

MAX_PAGE_CHARS = 12_000
MAX_LINKS = 150


async def _unreachable(crawler: Crawler, url: str) -> str | None:
    """Why a URL can't be used, or None if it loads with content."""
    if not url.startswith(("http://", "https://")):
        return "URL must start with http:// or https://."
    try:
        fetch = await crawler.fetch(url)
    except PlaywrightError as exc:
        return f"Could not load {url}: {exc.message.splitlines()[0]}"
    if not fetch.ok:
        return f"{url} returned HTTP {fetch.http_status} or no text; check the URL."
    return None


def build_read_page(crawler: Crawler) -> SdkMcpTool[Any]:
    @tool(
        "read_page",
        "Load a web page in a real browser and return its visible text and the links on it.",
        {"url": str},
    )
    async def read_page(args: dict[str, Any]) -> ToolResult:
        url = str(args.get("url", "")).strip()
        try:
            fetch = await crawler.fetch(url)
        except PlaywrightError as exc:
            return error(f"Could not load {url}: {exc.message.splitlines()[0]}")
        return text(
            {
                "url": fetch.url,
                "http_status": fetch.http_status,
                "text": truncate(fetch.text, MAX_PAGE_CHARS),
                "links": fetch.links[:MAX_LINKS],
            }
        )

    return read_page


SUGGESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "website": {"type": "string", "description": "Homepage URL."},
        "rationale": {
            "type": "string",
            "description": f"Becomes the competitor's notes: {COMPETITOR_NOTES}.",
        },
    },
    "required": ["name", "website", "rationale"],
}

PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "profile": {"type": "string", "description": "The company profile, under 250 words."},
    },
    "required": ["company_name", "profile"],
}


def build_company_tools(
    run_id: uuid.UUID, workspace_id: uuid.UUID, crawler: Crawler
) -> list[SdkMcpTool[Any]]:
    async def competitors(session) -> list[Competitor]:
        return list(
            (
                await session.scalars(
                    select(Competitor).where(Competitor.workspace_id == workspace_id)
                )
            ).all()
        )

    @tool(
        "get_workspace",
        "Get the company website, its current profile and the competitors already tracked.",
        {},
    )
    async def get_workspace(args: dict[str, Any]) -> ToolResult:
        async with SessionLocal() as session:
            workspace = await session.get(Workspace, workspace_id)
            tracked = await competitors(session)
        return text(
            {
                "website": workspace.website,
                "profile": workspace.company_profile or None,
                "tracked_competitors": [{"name": c.name, "website": c.website} for c in tracked],
            }
        )

    @tool(
        "save_profile",
        "Save the company name and profile. An existing profile is kept, never overwritten.",
        PROFILE_SCHEMA,
    )
    async def save_profile(args: dict[str, Any]) -> ToolResult:
        name = str(args.get("company_name", "")).strip()
        profile = str(args.get("profile", "")).strip()
        if not name or not profile:
            return error("company_name and profile are both required.")
        async with SessionLocal() as session:
            workspace = await session.get(Workspace, workspace_id)
            if workspace.name == DEFAULT_WORKSPACE_NAME:
                workspace.name = name[:200]
            kept = bool(workspace.company_profile.strip())
            if not kept:
                workspace.company_profile = profile
            await session.commit()
        if kept:
            return text("A profile already exists, so it was kept. Use it as written.")
        return text("Profile saved.")

    @tool(
        "suggest_competitor",
        "Propose one direct competitor for the human to approve.",
        SUGGESTION_SCHEMA,
    )
    async def suggest_competitor(args: dict[str, Any]) -> ToolResult:
        name = str(args.get("name", "")).strip()
        website = str(args.get("website", "")).strip()
        if not name or not website:
            return error("name and website are both required.")
        async with SessionLocal() as session:
            workspace = await session.get(Workspace, workspace_id)
            suggested = (
                await session.scalars(
                    select(CompetitorSuggestion).where(CompetitorSuggestion.run_id == run_id)
                )
            ).all()
            tracked = await competitors(session)
        if len(suggested) >= settings.discovery_max_competitors:
            return error(
                f"Already suggested {len(suggested)} competitors, the maximum. Submit your summary."
            )
        key = site_key(website)
        if workspace.website and key == site_key(workspace.website):
            return error("That's the company's own website.")
        if key in {site_key(c.website) for c in tracked}:
            return error(f"{website} is already tracked.")
        if key in {site_key(s.website) for s in suggested}:
            return error(f"{website} was already suggested in this run.")
        if problem := await _unreachable(crawler, website):
            return error(problem)
        async with SessionLocal() as session:
            session.add(
                CompetitorSuggestion(
                    run_id=run_id,
                    name=name[:200],
                    website=website[:500],
                    rationale=str(args.get("rationale", "")).strip(),
                )
            )
            await session.commit()
        return text(f"Suggested {name}.")

    @tool(
        "submit_summary",
        "Submit the run headline, under 15 words (e.g. 'Found 5 direct competitors to "
        "Tallybird'). Call exactly once, last.",
        {"headline": str},
    )
    async def submit_summary(args: dict[str, Any]) -> ToolResult:
        headline = str(args.get("headline", "")).strip()
        if not headline:
            return error("headline is required.")
        async with SessionLocal() as session:
            (await session.get(Run, run_id)).headline = headline[:500]
            await session.commit()
        return text("Summary saved. You're done.")

    return [
        build_read_page(crawler),
        get_workspace,
        save_profile,
        suggest_competitor,
        submit_summary,
    ]


PAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {"type": "string"},
        "page_type": {"type": "string", "enum": [t.value for t in PageType]},
        "rationale": {"type": "string", "description": "One sentence: what this page signals."},
    },
    "required": ["url", "page_type", "rationale"],
}


def build_page_tools(competitor_id: uuid.UUID, crawler: Crawler) -> list[SdkMcpTool[Any]]:
    @tool(
        "get_competitor",
        "Get the competitor, its notes, the pages already tracked and our own company profile.",
        {},
    )
    async def get_competitor(args: dict[str, Any]) -> ToolResult:
        async with SessionLocal() as session:
            competitor = await session.get(Competitor, competitor_id)
            workspace = await session.get(Workspace, competitor.workspace_id)
        return text(
            {
                "name": competitor.name,
                "website": competitor.website,
                "notes": competitor.notes or None,
                "tracked_pages": [
                    {"url": p.url, "page_type": p.page_type} for p in competitor.pages
                ],
                "our_profile": workspace.company_profile or None,
            }
        )

    @tool(
        "save_notes",
        "Save notes on who this competitor is. Existing notes are kept, never overwritten.",
        {
            "type": "object",
            "properties": {"notes": {"type": "string", "description": f"{COMPETITOR_NOTES}."}},
            "required": ["notes"],
        },
    )
    async def save_notes(args: dict[str, Any]) -> ToolResult:
        notes = str(args.get("notes", "")).strip()
        if not notes:
            return error("notes is required.")
        async with SessionLocal() as session:
            competitor = await session.get(Competitor, competitor_id)
            if competitor.notes.strip():
                return text("Notes already exist, so they were kept.")
            competitor.notes = notes
            await session.commit()
        return text("Notes saved.")

    @tool("add_page", "Start monitoring one page of this competitor's site.", PAGE_SCHEMA)
    async def add_page(args: dict[str, Any]) -> ToolResult:
        url = str(args.get("url", "")).strip()
        try:
            page_type = PageType(args.get("page_type"))
        except ValueError:
            return error("page_type must be one of the listed values.")
        async with SessionLocal() as session:
            competitor = await session.get(Competitor, competitor_id)
            count = await session.scalar(
                select(func.count())
                .select_from(TrackedPage)
                .where(TrackedPage.competitor_id == competitor_id)
            )
        if count >= settings.discovery_max_pages:
            return error(f"{count} pages are tracked, the maximum. You're done.")
        if not same_host(url, competitor.website):
            return error(f"Only pages on {competitor.website}'s own site can be tracked.")
        if site_key(url) in {site_key(p.url) for p in competitor.pages}:
            return error(f"{url} is already tracked.")
        if problem := await _unreachable(crawler, url):
            return error(problem)
        async with SessionLocal() as session:
            session.add(
                TrackedPage(
                    competitor_id=competitor_id,
                    url=url[:1000],
                    page_type=page_type,
                    rationale=str(args.get("rationale", "")).strip(),
                )
            )
            await session.commit()
        return text(f"Now tracking {url}.")

    return [build_read_page(crawler), get_competitor, save_notes, add_page]
