import uuid
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, Field

from app.models import PageType
from app.schemas.base import Schema


def _http_url(value: str) -> str:
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        raise ValueError("must start with http:// or https://")
    return value


HttpUrl = Annotated[str, Field(max_length=1000), AfterValidator(_http_url)]


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
