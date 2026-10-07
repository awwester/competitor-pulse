import uuid

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.api.deps import CurrentWorkspace, Session, Writable
from app.models import Competitor, TrackedPage
from app.schemas.competitor import (
    CompetitorIn,
    CompetitorOut,
    CompetitorUpdate,
    TrackedPageIn,
    TrackedPageOut,
    TrackedPageUpdate,
)

router = APIRouter(tags=["competitors"])


async def _get_competitor(
    session: Session, workspace: CurrentWorkspace, competitor_id: uuid.UUID
) -> Competitor:
    competitor = await session.get(Competitor, competitor_id)
    if competitor is None or competitor.workspace_id != workspace.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Competitor not found")
    return competitor


async def _get_page(
    session: Session, workspace: CurrentWorkspace, page_id: uuid.UUID
) -> TrackedPage:
    page = await session.get(TrackedPage, page_id)
    if page is None or page.competitor.workspace_id != workspace.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tracked page not found")
    return page


@router.get("/competitors", response_model=list[CompetitorOut])
async def list_competitors(session: Session, workspace: CurrentWorkspace):
    return (
        await session.scalars(
            select(Competitor)
            .where(Competitor.workspace_id == workspace.id)
            .order_by(Competitor.name)
        )
    ).all()


@router.post(
    "/competitors",
    response_model=CompetitorOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Writable],
)
async def create_competitor(body: CompetitorIn, session: Session, workspace: CurrentWorkspace):
    competitor = Competitor(
        workspace_id=workspace.id,
        name=body.name,
        website=body.website,
        notes=body.notes,
        pages=[TrackedPage(**page.model_dump()) for page in body.pages],
    )
    session.add(competitor)
    await session.commit()
    await session.refresh(competitor, ["pages"])
    return competitor


@router.patch("/competitors/{competitor_id}", response_model=CompetitorOut, dependencies=[Writable])
async def update_competitor(
    competitor_id: uuid.UUID, body: CompetitorUpdate, session: Session, workspace: CurrentWorkspace
):
    competitor = await _get_competitor(session, workspace, competitor_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(competitor, key, value)
    await session.commit()
    return competitor


@router.delete(
    "/competitors/{competitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Writable],
)
async def delete_competitor(
    competitor_id: uuid.UUID, session: Session, workspace: CurrentWorkspace
):
    await session.delete(await _get_competitor(session, workspace, competitor_id))
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/competitors/{competitor_id}/pages",
    response_model=TrackedPageOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Writable],
)
async def add_page(
    competitor_id: uuid.UUID, body: TrackedPageIn, session: Session, workspace: CurrentWorkspace
):
    competitor = await _get_competitor(session, workspace, competitor_id)
    page = TrackedPage(competitor_id=competitor.id, **body.model_dump())
    session.add(page)
    await session.commit()
    return page


@router.patch("/pages/{page_id}", response_model=TrackedPageOut, dependencies=[Writable])
async def update_page(
    page_id: uuid.UUID, body: TrackedPageUpdate, session: Session, workspace: CurrentWorkspace
):
    page = await _get_page(session, workspace, page_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(page, key, value)
    await session.commit()
    return page


@router.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Writable])
async def delete_page(page_id: uuid.UUID, session: Session, workspace: CurrentWorkspace):
    await session.delete(await _get_page(session, workspace, page_id))
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
