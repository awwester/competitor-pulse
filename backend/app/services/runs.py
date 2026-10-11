import uuid
from datetime import UTC, datetime

from sqlalchemy import exists, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db import SessionLocal
from app.models import (
    ACTIVE_STATUSES,
    Competitor,
    Run,
    RunKind,
    RunStatus,
    RunTrigger,
    TrackedPage,
    Workspace,
)
from app.services.errors import Conflict, NotFound


class RunAlreadyActive(Conflict):
    pass


class NothingToCheck(Conflict):
    pass


async def list_runs(session: AsyncSession, workspace_id: uuid.UUID, limit: int) -> list[Run]:
    return list(
        await session.scalars(
            select(Run)
            .where(Run.workspace_id == workspace_id)
            .order_by(Run.created_at.desc())
            .limit(limit)
        )
    )


async def get_owned_run(session: AsyncSession, workspace_id: uuid.UUID, run_id: uuid.UUID) -> Run:
    run = await session.get(Run, run_id)
    if run is None or run.workspace_id != workspace_id:
        raise NotFound("Run not found")
    return run


def require_review(run: Run, kind: RunKind | None = None) -> None:
    """Review actions apply to runs awaiting review, optionally only of one kind."""
    if kind and run.kind != kind:
        raise Conflict(f"Run is a {run.kind}, not a {kind}")
    if run.status != RunStatus.AWAITING_REVIEW:
        raise Conflict(f"Run is {run.status}, not awaiting review")


async def enqueue_run(
    session: AsyncSession,
    workspace_id: uuid.UUID,
    kind: RunKind = RunKind.CHECK,
    trigger: RunTrigger = RunTrigger.MANUAL,
    competitor_id: uuid.UUID | None = None,
) -> Run:
    """Add a queued run to the session (the caller commits).

    Raises RunAlreadyActive if the same job (kind and competitor) is already queued or running.
    """
    active = await session.scalar(
        select(Run.id)
        .where(
            Run.workspace_id == workspace_id,
            Run.kind == kind,
            Run.competitor_id.is_not_distinct_from(competitor_id),
            Run.status.in_(ACTIVE_STATUSES),
        )
        .limit(1)
    )
    if active:
        raise RunAlreadyActive(f"A {kind.replace('_', ' ')} is already queued or in progress")
    run = Run(
        workspace_id=workspace_id,
        kind=kind,
        trigger=trigger,
        competitor_id=competitor_id,
        status=RunStatus.QUEUED,
    )
    session.add(run)
    await session.flush()
    return run


async def enqueue_check(
    session: AsyncSession, workspace_id: uuid.UUID, trigger: RunTrigger = RunTrigger.MANUAL
) -> Run:
    """Queue a check (the caller commits). Raises NothingToCheck if no page is tracked."""
    tracked = await session.scalar(
        select(TrackedPage.id)
        .join(Competitor)
        .where(Competitor.workspace_id == workspace_id, TrackedPage.is_active)
        .limit(1)
    )
    if tracked is None:
        raise NothingToCheck("No pages are tracked yet. Add a competitor first")
    return await enqueue_run(session, workspace_id, RunKind.CHECK, trigger)


async def enqueue_company_discovery(session: AsyncSession, workspace_id: uuid.UUID) -> Run:
    """Queue a company discovery (the caller commits), unless a shortlist still awaits review."""
    awaiting = await session.scalar(
        select(Run.id)
        .where(
            Run.workspace_id == workspace_id,
            Run.kind == RunKind.COMPANY_DISCOVERY,
            Run.status == RunStatus.AWAITING_REVIEW,
        )
        .limit(1)
    )
    if awaiting:
        raise RunAlreadyActive("Review the suggested competitors first")
    return await enqueue_run(session, workspace_id, RunKind.COMPANY_DISCOVERY)


async def enqueue_checks(session: AsyncSession, trigger: RunTrigger) -> list[Run]:
    """Queue a check for every workspace, skipping any with nothing to check or a check active."""
    runs = []
    for workspace_id in (await session.scalars(select(Workspace.id))).all():
        try:
            runs.append(await enqueue_check(session, workspace_id, trigger))
        except Conflict:
            continue
    await session.commit()
    return runs


async def claim_next_run(session: AsyncSession) -> uuid.UUID | None:
    """Atomically move the oldest claimable queued run to running. Safe with multiple workers.

    A check waits while page discovery is active in its workspace, so it baselines the pages
    that discovery adds.
    """
    page_discovery = aliased(Run)
    next_queued = (
        select(Run.id)
        .where(
            Run.status == RunStatus.QUEUED,
            or_(
                Run.kind != RunKind.CHECK,
                ~exists().where(
                    page_discovery.workspace_id == Run.workspace_id,
                    page_discovery.kind == RunKind.PAGE_DISCOVERY,
                    page_discovery.status.in_(ACTIVE_STATUSES),
                ),
            ),
        )
        .order_by(Run.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
        .scalar_subquery()
    )
    run_id = await session.scalar(
        update(Run)
        .where(Run.id == next_queued)
        .values(status=RunStatus.RUNNING, started_at=datetime.now(UTC))
        .returning(Run.id)
    )
    await session.commit()
    return run_id


async def finish_run(run_id: uuid.UUID, **values) -> None:
    async with SessionLocal() as session:
        run = await session.get(Run, run_id)
        for key, value in values.items():
            setattr(run, key, value)
        run.finished_at = datetime.now(UTC)
        await session.commit()


async def fail_interrupted_runs(session: AsyncSession) -> int:
    """Runs left 'running' by a crashed worker will never finish; mark them failed on startup."""
    result = await session.execute(
        update(Run)
        .where(Run.status == RunStatus.RUNNING)
        .values(
            status=RunStatus.FAILED,
            error="Worker restarted while this run was in progress.",
            finished_at=datetime.now(UTC),
        )
    )
    await session.commit()
    return result.rowcount
