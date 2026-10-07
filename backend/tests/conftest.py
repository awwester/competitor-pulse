import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.api.deps import ensure_default_workspace
from app.config import settings
from app.db import SessionLocal, engine
from app.main import app
from app.models import Base, Workspace

assert settings.database_url.endswith("_test"), "Tests must run against the *_test database"


@pytest.fixture(scope="session", autouse=True)
async def schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
async def clean_tables():
    yield
    tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} CASCADE"))


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def workspace() -> Workspace:
    async with SessionLocal() as session:
        return await ensure_default_workspace(session)


@pytest.fixture
def demo_mode(monkeypatch):
    monkeypatch.setattr(settings, "demo_mode", True)
