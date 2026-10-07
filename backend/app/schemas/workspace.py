import uuid

from pydantic import EmailStr, Field

from app.schemas.base import Schema
from app.schemas.run import FindingOut, RunSummary


class WorkspaceOut(Schema):
    id: uuid.UUID
    name: str
    company_profile: str
    slack_webhook_url: str | None
    notify_emails: list[str]


class WorkspaceUpdate(Schema):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    company_profile: str | None = None
    slack_webhook_url: str | None = None
    notify_emails: list[EmailStr] | None = None


class MetaOut(Schema):
    demo_mode: bool
    agent_model: str
    schedule_cron: str


class DashboardOut(Schema):
    competitor_count: int
    page_count: int
    run_count: int
    total_cost_usd: float
    latest_run: RunSummary | None
    top_findings: list[FindingOut]
