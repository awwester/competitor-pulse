import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Finding, FindingCategory, Run
from app.services.errors import NotFound


async def get_owned_finding(
    session: AsyncSession, workspace_id: uuid.UUID, finding_id: uuid.UUID
) -> Finding:
    finding = await session.get(Finding, finding_id)
    if finding is None or finding.competitor.workspace_id != workspace_id:
        raise NotFound("Finding not found")
    return finding


async def search_findings(
    session: AsyncSession,
    workspace_id: uuid.UUID,
    *,
    competitor_id: uuid.UUID | None = None,
    category: FindingCategory | None = None,
    min_significance: int = 1,
    since: datetime | None = None,
    include_dismissed: bool = False,
    limit: int = 50,
) -> list[Finding]:
    """Most significant first, then newest."""
    query = (
        select(Finding)
        .join(Run)
        .where(Run.workspace_id == workspace_id, Finding.significance >= min_significance)
    )
    if competitor_id:
        query = query.where(Finding.competitor_id == competitor_id)
    if category:
        query = query.where(Finding.category == category)
    if since:
        query = query.where(Finding.created_at >= since)
    if not include_dismissed:
        query = query.where(Finding.is_dismissed.is_(False))
    query = query.order_by(Finding.significance.desc(), Finding.created_at.desc()).limit(limit)
    return list(await session.scalars(query))
