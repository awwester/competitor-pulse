from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentWorkspace, Session, Writable
from app.config import settings
from app.models import Competitor, Finding, Run, TrackedPage
from app.schemas.workspace import DashboardOut, MetaOut, WorkspaceOut, WorkspaceUpdate

router = APIRouter(tags=["workspace"])

TOP_FINDINGS_DAYS = 30


@router.get("/meta", response_model=MetaOut)
async def get_meta():
    return MetaOut(
        demo_mode=settings.demo_mode,
        agent_model=settings.agent_model,
        schedule_cron=settings.schedule_cron,
    )


@router.get("/workspace", response_model=WorkspaceOut)
async def get_workspace(workspace: CurrentWorkspace):
    return workspace


@router.patch("/workspace", response_model=WorkspaceOut, dependencies=[Writable])
async def update_workspace(body: WorkspaceUpdate, session: Session, workspace: CurrentWorkspace):
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(workspace, key, value)
    await session.commit()
    return workspace


@router.get("/dashboard", response_model=DashboardOut)
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
    latest_run = await session.scalar(
        select(Run).where(Run.workspace_id == workspace.id).order_by(Run.created_at.desc()).limit(1)
    )
    since = datetime.now(UTC) - timedelta(days=TOP_FINDINGS_DAYS)
    top_findings = (
        await session.scalars(
            select(Finding)
            .join(Run)
            .where(
                Run.workspace_id == workspace.id,
                Finding.created_at >= since,
                Finding.is_dismissed.is_(False),
            )
            .order_by(Finding.significance.desc(), Finding.created_at.desc())
            .limit(8)
        )
    ).all()
    return DashboardOut(
        competitor_count=competitor_count,
        page_count=page_count,
        run_count=run_count,
        total_cost_usd=total_cost,
        latest_run=latest_run,
        top_findings=top_findings,
    )
