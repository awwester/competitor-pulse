import uuid
from typing import Any, Self

from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import RunEvent, RunEventKind


class RunLog:
    """Appends trace events for a run, committing each one so the UI can follow along live."""

    def __init__(self, run_id: uuid.UUID, next_seq: int = 0) -> None:
        self.run_id = run_id
        self._seq = next_seq

    @classmethod
    async def for_run(cls, run_id: uuid.UUID) -> Self:
        async with SessionLocal() as session:
            last = await session.scalar(
                select(func.max(RunEvent.seq)).where(RunEvent.run_id == run_id)
            )
        return cls(run_id, next_seq=0 if last is None else last + 1)

    async def add(self, kind: RunEventKind, payload: dict[str, Any]) -> None:
        async with SessionLocal() as session:
            session.add(RunEvent(run_id=self.run_id, seq=self._seq, kind=kind, payload=payload))
            await session.commit()
        self._seq += 1

    async def phase(self, title: str, detail: str | None = None) -> None:
        await self.add(RunEventKind.PHASE, {"title": title, "detail": detail})

    async def error(self, message: str) -> None:
        await self.add(RunEventKind.ERROR, {"message": message})
