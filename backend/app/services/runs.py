import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.models import ACTIVE_STATUSES, Run, RunKind, RunStatus, RunTrigger, Workspace


class RunAlreadyActive(Exception):
    pass


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


async def enqueue_scheduled_runs(session: AsyncSession) -> list[Run]:
    runs = []
    for workspace_id in (await session.scalars(select(Workspace.id))).all():
        try:
            runs.append(await enqueue_run(session, workspace_id, trigger=RunTrigger.SCHEDULED))
        except RunAlreadyActive:
            continue
    await session.commit()
    return runs


async def claim_next_run(session: AsyncSession) -> uuid.UUID | None:
    """Atomically move the oldest queued run to running. Safe with multiple workers."""
    next_queued = (
        select(Run.id)
        .where(Run.status == RunStatus.QUEUED)
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
