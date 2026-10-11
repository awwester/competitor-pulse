import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Competitor, RunKind, TrackedPage
from app.schemas.competitor import CompetitorIn, TrackedPageIn
from app.services.errors import NotFound
from app.services.runs import enqueue_run


async def list_competitors(session: AsyncSession, workspace_id: uuid.UUID) -> list[Competitor]:
    return list(
        await session.scalars(
            select(Competitor)
            .where(Competitor.workspace_id == workspace_id)
            .order_by(Competitor.name)
        )
    )


async def get_owned_competitor(
    session: AsyncSession, workspace_id: uuid.UUID, competitor_id: uuid.UUID
) -> Competitor:
    competitor = await session.get(Competitor, competitor_id)
    if competitor is None or competitor.workspace_id != workspace_id:
        raise NotFound("Competitor not found")
    return competitor


async def get_owned_page(
    session: AsyncSession, workspace_id: uuid.UUID, page_id: uuid.UUID
) -> TrackedPage:
    page = await session.get(TrackedPage, page_id)
    if page is None or page.competitor.workspace_id != workspace_id:
        raise NotFound("Tracked page not found")
    return page


async def create_competitor(
    session: AsyncSession, workspace_id: uuid.UUID, body: CompetitorIn
) -> Competitor:
    """Without pages, the page discovery agent is queued to find them."""
    competitor = Competitor(
        workspace_id=workspace_id,
        name=body.name,
        website=body.website,
        notes=body.notes,
        pages=[TrackedPage(**page.model_dump()) for page in body.pages],
    )
    session.add(competitor)
    await session.flush()
    if not body.pages:
        await enqueue_run(
            session, workspace_id, RunKind.PAGE_DISCOVERY, competitor_id=competitor.id
        )
    await session.commit()
    await session.refresh(competitor, ["pages"])
    return competitor


async def add_page(
    session: AsyncSession, workspace_id: uuid.UUID, competitor_id: uuid.UUID, body: TrackedPageIn
) -> TrackedPage:
    competitor = await get_owned_competitor(session, workspace_id, competitor_id)
    page = TrackedPage(competitor_id=competitor.id, **body.model_dump())
    session.add(page)
    await session.commit()
    return page


async def delete_competitor(
    session: AsyncSession, workspace_id: uuid.UUID, competitor_id: uuid.UUID
) -> None:
    await session.delete(await get_owned_competitor(session, workspace_id, competitor_id))
    await session.commit()


async def delete_page(session: AsyncSession, workspace_id: uuid.UUID, page_id: uuid.UUID) -> None:
    await session.delete(await get_owned_page(session, workspace_id, page_id))
    await session.commit()
