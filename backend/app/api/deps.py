import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Workspace
from app.services import workspaces
from app.services.errors import ensure_writable

Session = Annotated[AsyncSession, Depends(get_session)]


async def get_workspace(workspace_id: uuid.UUID, session: Session) -> Workspace:
    """The workspace named in the URL."""
    return await workspaces.get_workspace(session, workspace_id)


CurrentWorkspace = Annotated[Workspace, Depends(get_workspace)]

Writable = Depends(ensure_writable)
