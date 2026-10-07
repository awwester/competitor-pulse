import uuid

from pydantic import Field

from app.schemas.base import HttpUrl, Schema


class DiscoveryIn(Schema):
    website: HttpUrl


class SuggestionIn(Schema):
    name: str = Field(min_length=1, max_length=200)
    website: HttpUrl


class SuggestionUpdate(Schema):
    is_selected: bool


class SuggestionOut(Schema):
    id: uuid.UUID
    name: str
    website: str
    rationale: str
    is_selected: bool
