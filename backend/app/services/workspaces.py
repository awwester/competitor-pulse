import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ACTIVE_STATUSES, Run, Workspace
from app.services.errors import Conflict, NotFound


async def list_workspaces(session: AsyncSession) -> list[Workspace]:
    return list(await session.scalars(select(Workspace).order_by(Workspace.created_at)))


async def get_workspace(session: AsyncSession, workspace_id: uuid.UUID) -> Workspace:
    """Add an access check here once there are accounts."""
    workspace = await session.get(Workspace, workspace_id)
    if workspace is None:
        raise NotFound("Workspace not found")
    return workspace


async def delete_workspace(session: AsyncSession, workspace: Workspace) -> None:
    active_run = await session.scalar(
        select(Run.id)
        .where(Run.workspace_id == workspace.id, Run.status.in_(ACTIVE_STATUSES))
        .limit(1)
    )
    if active_run:
        raise Conflict("Wait for the active run to finish")
    await session.delete(workspace)
    await session.commit()
