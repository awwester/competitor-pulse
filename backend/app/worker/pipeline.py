"""A run has two phases: a deterministic crawl/diff (cheap, no LLM) and, only if something
changed, the analyst agent."""

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from playwright.async_api import Error as PlaywrightError
from sqlalchemy import select

from app.agent.analyst import analyze_run
from app.config import settings
from app.db import SessionLocal
from app.models import Competitor, Run, RunStatus, Snapshot, TrackedPage, Workspace
from app.services.crawler import Crawler, PageFetch
from app.services.diffing import content_hash
from app.services.run_log import RunLog

logger = logging.getLogger(__name__)


async def _crawl(pages: list[TrackedPage], log: RunLog) -> dict[uuid.UUID, PageFetch]:
    semaphore = asyncio.Semaphore(settings.crawl_concurrency)
    results: dict[uuid.UUID, PageFetch] = {}

    async with Crawler() as crawler:

        async def fetch(page: TrackedPage) -> None:
            async with semaphore:
                try:
                    results[page.id] = await crawler.fetch(page.url)
                except PlaywrightError as exc:
                    await log.error(f"Could not fetch {page.url}: {exc.message.splitlines()[0]}")

        await asyncio.gather(*(fetch(page) for page in pages))
    return results


@dataclass(frozen=True)
class CrawlSummary:
    checked: int
    changed: int
    baselined: int


async def collect_snapshots(run: Run, log: RunLog) -> CrawlSummary:
    """Crawl every active page and store a snapshot where the text changed.

    A page's first snapshot is a baseline, not a change.
    """
    async with SessionLocal() as session:
        pages = list(
            (
                await session.scalars(
                    select(TrackedPage)
                    .join(Competitor)
                    .where(Competitor.workspace_id == run.workspace_id, TrackedPage.is_active)
                )
            ).all()
        )
    await log.phase("Crawling", f"Fetching {len(pages)} tracked pages")
    fetched = await _crawl(pages, log)

    changed = baselines = 0
    async with SessionLocal() as session:
        for page in pages:
            fetch = fetched.get(page.id)
            if fetch is None or not fetch.text:
                continue
            if fetch.http_status and fetch.http_status >= 400:
                # An error page isn't the competitor's content; don't let it register as a change.
                await log.error(f"{page.url} returned HTTP {fetch.http_status}; skipped")
                continue
            latest = await session.scalar(
                select(Snapshot)
                .where(Snapshot.tracked_page_id == page.id)
                .order_by(Snapshot.created_at.desc())
                .limit(1)
            )
            digest = content_hash(fetch.text)
            if latest and latest.content_hash == digest:
                continue
            session.add(
                Snapshot(
                    tracked_page_id=page.id,
                    run_id=run.id,
                    previous_id=latest.id if latest else None,
                    http_status=fetch.http_status,
                    content=fetch.text,
                    content_hash=digest,
                )
            )
            if latest:
                changed += 1
            else:
                baselines += 1
        await session.commit()

    detail = f"{changed} changed, {len(fetched) - changed - baselines} unchanged"
    if baselines:
        detail += f", {baselines} baselined (first capture)"
    await log.phase("Crawl complete", detail)
    return CrawlSummary(checked=len(fetched), changed=changed, baselined=baselines)


async def _finish(run_id: uuid.UUID, **values) -> None:
    async with SessionLocal() as session:
        run = await session.get(Run, run_id)
        for key, value in values.items():
            setattr(run, key, value)
        run.finished_at = datetime.now(UTC)
        await session.commit()


async def execute_run(run_id: uuid.UUID) -> None:
    log = await RunLog.for_run(run_id)
    async with SessionLocal() as session:
        run = await session.get(Run, run_id)
        workspace = await session.get(Workspace, run.workspace_id)

    try:
        crawl = await collect_snapshots(run, log)
        checked, changed = crawl.checked, crawl.changed
        if not changed:
            headline = (
                f"Baseline captured for {crawl.baselined} new pages"
                if crawl.baselined
                else "No changes detected"
            )
            await _finish(
                run_id, status=RunStatus.NO_CHANGES, pages_checked=checked, headline=headline
            )
            return

        await log.phase("Analyzing", f"Handing {changed} changed pages to the analyst agent")
        outcome = await analyze_run(workspace, run_id, changed, log)
        usage = vars(outcome.usage)

        async with SessionLocal() as session:
            has_report = bool((await session.get(Run, run_id)).report_markdown)

        if outcome.error or not has_report:
            error = outcome.error or "Agent finished without submitting a report."
            await log.error(error)
            await _finish(
                run_id,
                status=RunStatus.FAILED,
                error=error,
                pages_checked=checked,
                pages_changed=changed,
                **usage,
            )
            return

        await log.phase("Ready for review", "Approve the report to send it to your channels")
        await _finish(
            run_id,
            status=RunStatus.AWAITING_REVIEW,
            pages_checked=checked,
            pages_changed=changed,
            **usage,
        )
    except Exception as exc:
        logger.exception("Run %s failed", run_id)
        await log.error(f"{type(exc).__name__}: {exc}")
        await _finish(run_id, status=RunStatus.FAILED, error=str(exc))
