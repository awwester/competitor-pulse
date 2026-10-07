from sqlalchemy import func, select

from app.agent.discovery import discover_company, discover_pages
from app.db import SessionLocal
from app.models import Competitor, Run, RunStatus, TrackedPage, Workspace
from app.services.run_log import RunLog
from app.worker.finish import finish_agent_run


async def _page_count(competitor: Competitor) -> int:
    async with SessionLocal() as session:
        return await session.scalar(
            select(func.count())
            .select_from(TrackedPage)
            .where(TrackedPage.competitor_id == competitor.id)
        )


async def execute_company_discovery(run: Run, workspace: Workspace, log: RunLog) -> None:
    await log.phase("Discovering", f"Reading {workspace.website} and looking for competitors")
    outcome = await discover_company(workspace, run.id, log)
    async with SessionLocal() as session:
        run = await session.get(Run, run.id)
    await finish_agent_run(
        run.id,
        outcome,
        log,
        missing=None if run.headline else "Agent finished without submitting a summary.",
        status=RunStatus.AWAITING_REVIEW,
        phase=("Ready for review", "Choose which competitors to track"),
    )


async def execute_page_discovery(run: Run, workspace: Workspace, log: RunLog) -> None:
    async with SessionLocal() as session:
        competitor = await session.get(Competitor, run.competitor_id)
    before = await _page_count(competitor)
    await log.phase("Finding pages", f"Reading {competitor.website}")
    outcome = await discover_pages(competitor, log)
    added = await _page_count(competitor) - before
    headline = (
        f"Added {added} page{'' if added == 1 else 's'} for {competitor.name}"
        if added
        else f"No new pages found for {competitor.name}"
    )
    await finish_agent_run(
        run.id,
        outcome,
        log,
        missing=None,
        status=RunStatus.COMPLETED,
        phase=("Done", headline),
        headline=headline,
    )
