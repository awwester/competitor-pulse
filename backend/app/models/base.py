import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSONB}


class BaseEntity(Base):
    """UUID primary key plus created/updated timestamps on every table."""

    __abstract__ = True
    # Fetch server-generated timestamps via RETURNING so async code never lazy-loads them.
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


def str_enum(enum_cls: type[StrEnum]) -> SAEnum:
    """Store a StrEnum as its value in a VARCHAR column."""
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=32,
        values_callable=lambda members: [m.value for m in members],
    )
