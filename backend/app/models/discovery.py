import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class CompetitorSuggestion(BaseEntity):
    """A competitor proposed by company discovery (or typed in during review), pending approval."""

    __tablename__ = "competitor_suggestions"

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    website: Mapped[str] = mapped_column(String(500))
    rationale: Mapped[str] = mapped_column(Text, default="")
    is_selected: Mapped[bool] = mapped_column(default=True)
