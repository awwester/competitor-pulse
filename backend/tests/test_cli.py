from sqlalchemy import func, select

from app.cli import seed_demo
from app.db import SessionLocal
from app.models import Competitor, Workspace


async def test_seed_demo_creates_the_tallybird_company():
    await seed_demo()
    async with SessionLocal() as session:
        workspace = await session.scalar(select(Workspace))
        competitors = await session.scalar(select(func.count()).select_from(Competitor))
    assert (workspace.name, competitors) == ("Tallybird", 2)


async def test_seed_demo_twice_adds_nothing_more():
    await seed_demo()
    await seed_demo()
    async with SessionLocal() as session:
        assert await session.scalar(select(func.count()).select_from(Workspace)) == 1
