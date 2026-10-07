from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity

DEFAULT_WORKSPACE_NAME = "My Company"


class Workspace(BaseEntity):
    """Tenant boundary. v1 runs single-tenant, but every row is scoped to a workspace."""

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(200))
    website: Mapped[str | None] = mapped_column(String(500))
    company_profile: Mapped[str] = mapped_column(Text, default="")
    slack_webhook_url: Mapped[str | None] = mapped_column(String(500))
    notify_emails: Mapped[list[str]] = mapped_column(ARRAY(String(320)), default=list)
