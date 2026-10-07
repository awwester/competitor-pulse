import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity, str_enum


class PageType(StrEnum):
    PRICING = "pricing"
    CHANGELOG = "changelog"
    BLOG = "blog"
    HOMEPAGE = "homepage"
    CAREERS = "careers"
    DOCS = "docs"
    OTHER = "other"


class Competitor(BaseEntity):
    __tablename__ = "competitors"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    website: Mapped[str] = mapped_column(String(500))
    notes: Mapped[str] = mapped_column(Text, default="")

    pages: Mapped[list["TrackedPage"]] = relationship(
        back_populates="competitor",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TrackedPage.created_at",
    )


class TrackedPage(BaseEntity):
    __tablename__ = "tracked_pages"

    competitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("competitors.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String(1000))
    page_type: Mapped[PageType] = mapped_column(str_enum(PageType), default=PageType.OTHER)
    is_active: Mapped[bool] = mapped_column(default=True)

    competitor: Mapped[Competitor] = relationship(back_populates="pages", lazy="joined")
