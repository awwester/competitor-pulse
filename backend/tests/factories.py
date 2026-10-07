"""Small async builders for test data. Each commits and returns the created row."""

from dataclasses import dataclass

from app.db import SessionLocal
from app.models import (
    Competitor,
    Finding,
    FindingCategory,
    PageType,
    Run,
    RunStatus,
    Snapshot,
    TrackedPage,
    Workspace,
)
from app.services.diffing import content_hash


async def create_competitor(
    workspace: Workspace,
    name: str = "Acme",
    page_urls: tuple[str, ...] = ("https://acme.test/pricing",),
    page_type: PageType = PageType.PRICING,
) -> Competitor:
    async with SessionLocal() as session:
        competitor = Competitor(
            workspace_id=workspace.id,
            name=name,
            website="https://acme.test",
            pages=[TrackedPage(url=url, page_type=page_type) for url in page_urls],
        )
        session.add(competitor)
        await session.commit()
        await session.refresh(competitor, ["pages"])
        return competitor


async def create_run(workspace: Workspace, status: RunStatus = RunStatus.QUEUED, **fields) -> Run:
    async with SessionLocal() as session:
        run = Run(workspace_id=workspace.id, status=status, **fields)
        session.add(run)
        await session.commit()
        return run


async def create_snapshot(
    page: TrackedPage, content: str, run: Run | None = None, previous: Snapshot | None = None
) -> Snapshot:
    async with SessionLocal() as session:
        snapshot = Snapshot(
            tracked_page_id=page.id,
            run_id=run.id if run else None,
            previous_id=previous.id if previous else None,
            content=content,
            content_hash=content_hash(content),
        )
        session.add(snapshot)
        await session.commit()
        return snapshot


@dataclass
class ChangedPage:
    competitor: Competitor
    page: TrackedPage
    run: Run


async def create_changed_page(
    workspace: Workspace, before: str, after: str, status: RunStatus = RunStatus.RUNNING
) -> ChangedPage:
    """A competitor page with a baseline snapshot and a changed snapshot in a run."""
    competitor = await create_competitor(workspace)
    page = competitor.pages[0]
    baseline = await create_snapshot(page, before)
    run = await create_run(workspace, status)
    await create_snapshot(page, after, run=run, previous=baseline)
    return ChangedPage(competitor=competitor, page=page, run=run)


async def create_finding(changed: ChangedPage, **overrides) -> Finding:
    fields = {
        "category": FindingCategory.PRICING,
        "significance": 4,
        "title": "Pro plan price cut",
        "summary": "Pro dropped from $35 to $29.",
        "evidence": "$29 / month",
        **overrides,
    }
    async with SessionLocal() as session:
        finding = Finding(
            run_id=changed.run.id,
            competitor_id=changed.competitor.id,
            tracked_page_id=changed.page.id,
            **fields,
        )
        session.add(finding)
        await session.commit()
        return finding
