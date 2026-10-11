from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Response, status
from sqlalchemy import func, select

from app.api.deps import CurrentWorkspace, Session, Writable
from app.config import settings
from app.models import (
    Competitor,
    Run,
    RunKind,
    RunStatus,
    TrackedPage,
    Workspace,
)
from app.schemas.workspace import (
    DashboardOut,
    MetaOut,
    WorkspaceIn,
    WorkspaceOut,
    WorkspaceUpdate,
)
from app.services import workspaces
from app.services.findings import search_findings
from app.services.runs import enqueue_company_discovery
from app.services.schedule import next_check_at

router = APIRouter(tags=["workspace"])
# Mounted under /workspaces/{workspace_id}.
scoped_router = APIRouter(tags=["workspace"])

TOP_FINDINGS_DAYS = 30


@router.get("/meta", response_model=MetaOut)
async def get_meta():
    return MetaOut(
        demo_mode=settings.demo_mode,
        agent_model=settings.agent_model,
        agent_configured=bool(settings.anthropic_api_key),
        sample_company_url=settings.sample_company_url or None,
        next_check_at=next_check_at(),
    )


@router.get("/workspaces", response_model=list[WorkspaceOut])
async def list_workspaces(session: Session):
    return await workspaces.list_workspaces(session)


@router.post(
    "/workspaces",
    response_model=WorkspaceOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Writable],
)
async def create_workspace(body: WorkspaceIn, session: Session):
    """Add a company and start discovery from its website, which also names it."""
    workspace = Workspace(website=body.website, notify_emails=[])
    session.add(workspace)
    await session.flush()
    await enqueue_company_discovery(session, workspace.id)
    await session.commit()
    return workspace


@scoped_router.get("", response_model=WorkspaceOut)
async def get_workspace(workspace: CurrentWorkspace):
    return workspace


@scoped_router.patch("", response_model=WorkspaceOut, dependencies=[Writable])
async def update_workspace(body: WorkspaceUpdate, session: Session, workspace: CurrentWorkspace):
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(workspace, key, value)
    await session.commit()
    return workspace


@scoped_router.delete("", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Writable])
async def delete_workspace(session: Session, workspace: CurrentWorkspace):
    await workspaces.delete_workspace(session, workspace)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@scoped_router.get("/dashboard", response_model=DashboardOut)
async def get_dashboard(session: Session, workspace: CurrentWorkspace):
    competitor_count = await session.scalar(
        select(func.count()).select_from(Competitor).where(Competitor.workspace_id == workspace.id)
    )
    page_count = await session.scalar(
        select(func.count())
        .select_from(TrackedPage)
        .join(Competitor)
        .where(Competitor.workspace_id == workspace.id, TrackedPage.is_active)
    )
    run_count, total_cost = (
        await session.execute(
            select(func.count(), func.coalesce(func.sum(Run.cost_usd), 0.0)).where(
                Run.workspace_id == workspace.id
            )
        )
    ).one()
    latest_check = await session.scalar(
        select(Run)
        .where(Run.workspace_id == workspace.id, Run.kind == RunKind.CHECK)
        .order_by(Run.created_at.desc())
        .limit(1)
    )
    pending_reviews = await session.scalars(
        select(Run)
        .where(Run.workspace_id == workspace.id, Run.status == RunStatus.AWAITING_REVIEW)
        .order_by(Run.created_at.desc())
    )
    since = datetime.now(UTC) - timedelta(days=TOP_FINDINGS_DAYS)
    top_findings = await search_findings(session, workspace.id, since=since, limit=8)
    return DashboardOut(
        competitor_count=competitor_count,
        page_count=page_count,
        run_count=run_count,
        total_cost_usd=total_cost,
        latest_check=latest_check,
        pending_reviews=list(pending_reviews),
        top_findings=top_findings,
    )
