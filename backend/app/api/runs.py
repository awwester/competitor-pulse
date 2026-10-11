import uuid

from fastapi import APIRouter, Query, status
from sqlalchemy import select

from app.api.deps import CurrentWorkspace, Session, Writable
from app.models import RunEvent, RunKind, RunStatus
from app.schemas.run import FindingOut, FindingUpdate, RunDetail, RunEventOut, RunSummary
from app.services.findings import get_owned_finding
from app.services.notifier import build_digest, deliver
from app.services.run_log import RunLog
from app.services.runs import enqueue_check, get_owned_run, list_runs, require_review

router = APIRouter(tags=["runs"])


@router.get("/runs", response_model=list[RunSummary])
async def get_runs(session: Session, workspace: CurrentWorkspace, limit: int = Query(50, le=200)):
    return await list_runs(session, workspace.id, limit)


@router.post(
    "/runs", response_model=RunSummary, status_code=status.HTTP_201_CREATED, dependencies=[Writable]
)
async def create_run(session: Session, workspace: CurrentWorkspace):
    run = await enqueue_check(session, workspace.id)
    await session.commit()
    return run


@router.get("/runs/{run_id}", response_model=RunDetail)
async def get_run(run_id: uuid.UUID, session: Session, workspace: CurrentWorkspace):
    return await get_owned_run(session, workspace.id, run_id)


@router.get("/runs/{run_id}/events", response_model=list[RunEventOut])
async def list_run_events(
    run_id: uuid.UUID, session: Session, workspace: CurrentWorkspace, after: int = -1
):
    await get_owned_run(session, workspace.id, run_id)
    return (
        await session.scalars(
            select(RunEvent)
            .where(RunEvent.run_id == run_id, RunEvent.seq > after)
            .order_by(RunEvent.seq)
        )
    ).all()


@router.post("/runs/{run_id}/publish", response_model=RunDetail, dependencies=[Writable])
async def publish_run(run_id: uuid.UUID, session: Session, workspace: CurrentWorkspace):
    """Human-in-the-loop gate: nothing leaves the system until a reviewer approves the report."""
    run = await get_owned_run(session, workspace.id, run_id)
    require_review(run, RunKind.CHECK)
    findings = [f for f in run.findings if not f.is_dismissed]
    delivered, errors = await deliver(workspace, build_digest(run, findings))

    log = await RunLog.for_run(run.id)
    for error in errors:
        await log.error(error)
    await log.phase(
        "Published", f"Sent to {', '.join(delivered)}" if delivered else "No channels configured"
    )

    run.status = RunStatus.PUBLISHED
    await session.commit()
    return run


@router.post("/runs/{run_id}/dismiss", response_model=RunDetail, dependencies=[Writable])
async def dismiss_run(run_id: uuid.UUID, session: Session, workspace: CurrentWorkspace):
    run = await get_owned_run(session, workspace.id, run_id)
    require_review(run)
    run.status = RunStatus.DISMISSED
    await session.commit()
    return run


@router.patch("/findings/{finding_id}", response_model=FindingOut, dependencies=[Writable])
async def update_finding(
    finding_id: uuid.UUID, body: FindingUpdate, session: Session, workspace: CurrentWorkspace
):
    finding = await get_owned_finding(session, workspace.id, finding_id)
    finding.is_dismissed = body.is_dismissed
    await session.commit()
    return finding
