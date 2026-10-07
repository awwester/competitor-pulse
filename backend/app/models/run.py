import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity, str_enum
from app.models.competitor import Competitor, TrackedPage


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"
    PUBLISHED = "published"
    DISMISSED = "dismissed"
    NO_CHANGES = "no_changes"
    FAILED = "failed"


class RunTrigger(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class RunEventKind(StrEnum):
    PHASE = "phase"
    TEXT = "text"
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    RESULT = "result"


class FindingCategory(StrEnum):
    PRICING = "pricing"
    PRODUCT = "product"
    POSITIONING = "positioning"
    HIRING = "hiring"
    CONTENT = "content"
    OTHER = "other"


class Run(BaseEntity):
    __tablename__ = "runs"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[RunStatus] = mapped_column(
        str_enum(RunStatus), default=RunStatus.QUEUED, index=True
    )
    trigger: Mapped[RunTrigger] = mapped_column(str_enum(RunTrigger), default=RunTrigger.MANUAL)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    headline: Mapped[str | None] = mapped_column(String(500))
    report_markdown: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)

    pages_checked: Mapped[int] = mapped_column(default=0)
    pages_changed: Mapped[int] = mapped_column(default=0)

    num_turns: Mapped[int] = mapped_column(default=0)
    input_tokens: Mapped[int] = mapped_column(default=0)
    output_tokens: Mapped[int] = mapped_column(default=0)
    cache_read_tokens: Mapped[int] = mapped_column(default=0)
    cache_write_tokens: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(default=0.0)

    findings: Mapped[list["Finding"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by=lambda: (Finding.significance.desc(), Finding.created_at),
    )


class RunEvent(BaseEntity):
    """One step of the agent trace: a phase marker, model text, tool call or tool result."""

    __tablename__ = "run_events"
    __table_args__ = (UniqueConstraint("run_id", "seq"),)

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    seq: Mapped[int]
    kind: Mapped[RunEventKind] = mapped_column(str_enum(RunEventKind))
    payload: Mapped[dict[str, Any]] = mapped_column(default=dict)


class Finding(BaseEntity):
    __tablename__ = "findings"

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("competitors.id", ondelete="CASCADE"), index=True
    )
    tracked_page_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tracked_pages.id", ondelete="SET NULL")
    )
    category: Mapped[FindingCategory] = mapped_column(str_enum(FindingCategory))
    significance: Mapped[int] = mapped_column(SmallInteger)
    title: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text, default="")
    recommended_action: Mapped[str] = mapped_column(Text, default="")
    is_dismissed: Mapped[bool] = mapped_column(default=False)

    competitor: Mapped[Competitor] = relationship(lazy="joined")
    tracked_page: Mapped[TrackedPage | None] = relationship(lazy="joined")

    @property
    def competitor_name(self) -> str:
        return self.competitor.name

    @property
    def source_url(self) -> str | None:
        return self.tracked_page.url if self.tracked_page else None
