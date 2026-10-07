import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentWorkspace, Session, Writable
from app.api.runs import enqueue, get_owned_run, require_review
from app.models import Competitor, CompetitorSuggestion, Run, RunKind, RunStatus
from app.schemas.discovery import DiscoveryIn, SuggestionIn, SuggestionOut, SuggestionUpdate
from app.schemas.run import RunDetail, RunSummary
from app.services.run_log import RunLog
from app.services.runs import RunAlreadyActive, enqueue_run
from app.services.urls import site_key

router = APIRouter(tags=["discovery"])


@router.post(
    "/discovery",
    response_model=RunSummary,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Writable],
)
async def start_discovery(body: DiscoveryIn, session: Session, workspace: CurrentWorkspace):
    """Profile the company from its website and suggest competitors to review."""
    workspace.website = body.website
    run = await enqueue(session, workspace, RunKind.COMPANY_DISCOVERY)
    await session.commit()
    return run


@router.post(
    "/runs/{run_id}/suggestions",
    response_model=SuggestionOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Writable],
)
async def add_suggestion(
    run_id: uuid.UUID, body: SuggestionIn, session: Session, workspace: CurrentWorkspace
):
    """A competitor the reviewer knows about that the agent missed."""
    run = await get_owned_run(session, workspace, run_id)
    require_review(run, RunKind.COMPANY_DISCOVERY)
    suggestion = CompetitorSuggestion(run_id=run.id, name=body.name, website=body.website)
    session.add(suggestion)
    await session.commit()
    return suggestion


@router.patch("/suggestions/{suggestion_id}", response_model=SuggestionOut, dependencies=[Writable])
async def update_suggestion(
    suggestion_id: uuid.UUID, body: SuggestionUpdate, session: Session, workspace: CurrentWorkspace
):
    suggestion = await session.get(CompetitorSuggestion, suggestion_id)
    run = suggestion and await session.get(Run, suggestion.run_id)
    if run is None or run.workspace_id != workspace.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Suggestion not found")
    require_review(run, RunKind.COMPANY_DISCOVERY)
    suggestion.is_selected = body.is_selected
    await session.commit()
    return suggestion


@router.post("/runs/{run_id}/apply", response_model=RunDetail, dependencies=[Writable])
async def apply_discovery(run_id: uuid.UUID, session: Session, workspace: CurrentWorkspace):
    """Human-in-the-loop gate: track the approved competitors, then find their pages and
    capture a baseline."""
    run = await get_owned_run(session, workspace, run_id)
    require_review(run, RunKind.COMPANY_DISCOVERY)
    tracked = {
        site_key(website)
        for website in await session.scalars(
            select(Competitor.website).where(Competitor.workspace_id == workspace.id)
        )
    }
    competitors = [
        Competitor(workspace_id=workspace.id, name=s.name, website=s.website, notes=s.rationale)
        for s in run.suggestions
        if s.is_selected and site_key(s.website) not in tracked
    ]
    session.add_all(competitors)
    await session.flush()
    for competitor in competitors:
        await enqueue_run(
            session, workspace.id, RunKind.PAGE_DISCOVERY, competitor_id=competitor.id
        )
    run.status = RunStatus.APPLIED
    await session.commit()
    if competitors:
        # A check queued after the page discoveries baselines the pages they find. It gets its
        # own transaction because created_at (the queue order) is fixed per transaction.
        try:
            await enqueue_run(session, workspace.id, RunKind.CHECK)
            await session.commit()
        except RunAlreadyActive:
            pass

    detail = f"Tracking {len(competitors)} new competitor{'' if len(competitors) == 1 else 's'}"
    await (await RunLog.for_run(run.id)).phase("Applied", detail)
    return run
