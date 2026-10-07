import uuid
from datetime import datetime
from typing import Any

from app.models import FindingCategory, RunEventKind, RunStatus, RunTrigger
from app.schemas.base import Schema


class FindingOut(Schema):
    id: uuid.UUID
    run_id: uuid.UUID
    competitor_id: uuid.UUID
    competitor_name: str
    tracked_page_id: uuid.UUID | None
    source_url: str | None
    category: FindingCategory
    significance: int
    title: str
    summary: str
    evidence: str
    recommended_action: str
    is_dismissed: bool
    created_at: datetime


class FindingUpdate(Schema):
    is_dismissed: bool


class RunSummary(Schema):
    id: uuid.UUID
    status: RunStatus
    trigger: RunTrigger
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    headline: str | None
    pages_checked: int
    pages_changed: int
    num_turns: int
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    cost_usd: float


class RunDetail(RunSummary):
    report_markdown: str | None
    error: str | None
    findings: list[FindingOut]


class RunEventOut(Schema):
    id: uuid.UUID
    seq: int
    kind: RunEventKind
    payload: dict[str, Any]
    created_at: datetime
