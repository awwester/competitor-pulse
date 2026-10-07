import uuid

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import CurrentWorkspace, Session, Writable
from app.models import Finding, Run, RunEvent, RunStatus
from app.schemas.run import FindingOut, FindingUpdate, RunDetail, RunEventOut, RunSummary
from app.services.notifier import build_digest, deliver
from app.services.run_log import RunLog
from app.services.runs import enqueue_run

router = APIRouter(tags=["runs"])


async def _get_run(session: Session, workspace: CurrentWorkspace, run_id: uuid.UUID) -> Run:
    run = await session.get(Run, run_id)
    if run is None or run.workspace_id != workspace.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Run not found")
    return run


def _require_review(run: Run) -> None:
    if run.status != RunStatus.AWAITING_REVIEW:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Run is {run.status}, not awaiting review")


@router.get("/runs", response_model=list[RunSummary])
async def list_runs(session: Session, workspace: CurrentWorkspace, limit: int = Query(50, le=200)):
    return (
        await session.scalars(
            select(Run)
            .where(Run.workspace_id == workspace.id)
            .order_by(Run.created_at.desc())
            .limit(limit)
        )
    ).all()


@router.post(
    "/runs", response_model=RunSummary, status_code=status.HTTP_201_CREATED, dependencies=[Writable]
)
async def create_run(session: Session, workspace: CurrentWorkspace):
    active = await session.scalar(
        select(Run.id).where(
            Run.workspace_id == workspace.id,
            Run.status.in_([RunStatus.QUEUED, RunStatus.RUNNING]),
        )
    )
    if active:
        raise HTTPException(status.HTTP_409_CONFLICT, "A run is already queued or in progress")
    return await enqueue_run(session, workspace.id)


@router.get("/runs/{run_id}", response_model=RunDetail)
async def get_run(run_id: uuid.UUID, session: Session, workspace: CurrentWorkspace):
    return await _get_run(session, workspace, run_id)


@router.get("/runs/{run_id}/events", response_model=list[RunEventOut])
async def list_run_events(
    run_id: uuid.UUID, session: Session, workspace: CurrentWorkspace, after: int = -1
):
    await _get_run(session, workspace, run_id)
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
    run = await _get_run(session, workspace, run_id)
    _require_review(run)
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
    run = await _get_run(session, workspace, run_id)
    _require_review(run)
    run.status = RunStatus.DISMISSED
    await session.commit()
    return run


@router.patch("/findings/{finding_id}", response_model=FindingOut, dependencies=[Writable])
async def update_finding(
    finding_id: uuid.UUID, body: FindingUpdate, session: Session, workspace: CurrentWorkspace
):
    finding = await session.get(Finding, finding_id)
    if finding is None or finding.competitor.workspace_id != workspace.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Finding not found")
    finding.is_dismissed = body.is_dismissed
    await session.commit()
    return finding
