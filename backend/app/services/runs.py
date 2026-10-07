import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Run, RunStatus, RunTrigger, Workspace


async def enqueue_run(
    session: AsyncSession, workspace_id: uuid.UUID, trigger: RunTrigger = RunTrigger.MANUAL
) -> Run:
    run = Run(workspace_id=workspace_id, trigger=trigger, status=RunStatus.QUEUED)
    session.add(run)
    await session.commit()
    return run


async def enqueue_scheduled_runs(session: AsyncSession) -> list[Run]:
    workspace_ids = (await session.scalars(select(Workspace.id))).all()
    return [await enqueue_run(session, wid, RunTrigger.SCHEDULED) for wid in workspace_ids]


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
