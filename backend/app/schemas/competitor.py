import uuid
from datetime import datetime

from pydantic import Field

from app.models import PageType
from app.schemas.base import HttpUrl, Schema


class TrackedPageIn(Schema):
    url: HttpUrl
    page_type: PageType = PageType.OTHER
    is_active: bool = True


class TrackedPageUpdate(Schema):
    url: HttpUrl | None = None
    page_type: PageType | None = None
    is_active: bool | None = None


class TrackedPageOut(Schema):
    id: uuid.UUID
    competitor_id: uuid.UUID
    url: str
    page_type: PageType
    is_active: bool
    rationale: str
    created_at: datetime


class CompetitorIn(Schema):
    name: str = Field(min_length=1, max_length=200)
    website: HttpUrl
    notes: str = ""
    pages: list[TrackedPageIn] = []


class CompetitorUpdate(Schema):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    website: HttpUrl | None = None
    notes: str | None = None


class CompetitorOut(Schema):
    id: uuid.UUID
    name: str
    website: str
    notes: str
    created_at: datetime
    pages: list[TrackedPageOut]
