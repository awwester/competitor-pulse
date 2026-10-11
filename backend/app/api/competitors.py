import uuid

from fastapi import APIRouter, Response, status

from app.api.deps import CurrentWorkspace, Session, Writable
from app.models import RunKind
from app.schemas.competitor import (
    CompetitorIn,
    CompetitorOut,
    CompetitorUpdate,
    TrackedPageIn,
    TrackedPageOut,
    TrackedPageUpdate,
)
from app.schemas.run import RunSummary
from app.services import competitors
from app.services.competitors import get_owned_competitor, get_owned_page
from app.services.runs import enqueue_run

router = APIRouter(tags=["competitors"])


@router.get("/competitors", response_model=list[CompetitorOut])
async def list_competitors(session: Session, workspace: CurrentWorkspace):
    return await competitors.list_competitors(session, workspace.id)


@router.post(
    "/competitors",
    response_model=CompetitorOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Writable],
)
async def create_competitor(body: CompetitorIn, session: Session, workspace: CurrentWorkspace):
    return await competitors.create_competitor(session, workspace.id, body)


@router.post(
    "/competitors/{competitor_id}/discover",
    response_model=RunSummary,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Writable],
)
async def discover_pages(competitor_id: uuid.UUID, session: Session, workspace: CurrentWorkspace):
    competitor = await get_owned_competitor(session, workspace.id, competitor_id)
    run = await enqueue_run(
        session, workspace.id, RunKind.PAGE_DISCOVERY, competitor_id=competitor.id
    )
    await session.commit()
    return run


@router.patch("/competitors/{competitor_id}", response_model=CompetitorOut, dependencies=[Writable])
async def update_competitor(
    competitor_id: uuid.UUID, body: CompetitorUpdate, session: Session, workspace: CurrentWorkspace
):
    competitor = await get_owned_competitor(session, workspace.id, competitor_id)
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
    await competitors.delete_competitor(session, workspace.id, competitor_id)
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
    return await competitors.add_page(session, workspace.id, competitor_id, body)


@router.patch("/pages/{page_id}", response_model=TrackedPageOut, dependencies=[Writable])
async def update_page(
    page_id: uuid.UUID, body: TrackedPageUpdate, session: Session, workspace: CurrentWorkspace
):
    page = await get_owned_page(session, workspace.id, page_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(page, key, value)
    await session.commit()
    return page


@router.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Writable])
async def delete_page(page_id: uuid.UUID, session: Session, workspace: CurrentWorkspace):
    await competitors.delete_page(session, workspace.id, page_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
