import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class Snapshot(BaseEntity):
    """Normalized visible text of a tracked page, written only when the text changes."""

    __tablename__ = "snapshots"
    __table_args__ = (Index("ix_snapshots_page_created", "tracked_page_id", "created_at"),)

    tracked_page_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tracked_pages.id", ondelete="CASCADE")
    )
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("runs.id", ondelete="SET NULL"), index=True
    )
    previous_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("snapshots.id", ondelete="SET NULL")
    )
    http_status: Mapped[int | None] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
