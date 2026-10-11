import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.models import DEFAULT_WORKSPACE_NAME, Workspace

Session = Annotated[AsyncSession, Depends(get_session)]


async def ensure_default_workspace(session: AsyncSession) -> Workspace:
    workspace = await session.scalar(select(Workspace).order_by(Workspace.created_at).limit(1))
    if workspace is None:
        workspace = Workspace(name=DEFAULT_WORKSPACE_NAME, notify_emails=[])
        session.add(workspace)
        await session.commit()
    return workspace


async def get_workspace(workspace_id: uuid.UUID, session: Session) -> Workspace:
    """The workspace named in the URL. Add an access check here once there are accounts."""
    workspace = await session.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Workspace not found")
    return workspace


CurrentWorkspace = Annotated[Workspace, Depends(get_workspace)]


def require_writable() -> None:
    if settings.demo_mode:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This is a read-only demo.")


Writable = Depends(require_writable)
