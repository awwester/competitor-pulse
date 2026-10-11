import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.base import HttpUrl, Schema
from app.schemas.run import FindingOut, RunSummary


class WorkspaceOut(Schema):
    id: uuid.UUID
    name: str
    website: str | None
    company_profile: str
    slack_configured: bool
    notify_emails: list[str]


class WorkspaceIn(Schema):
    website: HttpUrl


class WorkspaceUpdate(Schema):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    website: HttpUrl | None = None
    company_profile: str | None = None
    slack_webhook_url: str | None = None
    notify_emails: list[EmailStr] | None = None


class MetaOut(Schema):
    demo_mode: bool
    agent_model: str
    agent_configured: bool
    sample_company_url: str | None
    next_check_at: datetime | None


class DashboardOut(Schema):
    competitor_count: int
    page_count: int
    run_count: int
    total_cost_usd: float
    latest_check: RunSummary | None
    pending_reviews: list[RunSummary]
    top_findings: list[FindingOut]
