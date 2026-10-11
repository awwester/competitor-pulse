import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.config import settings
from app.db import engine
from app.main import app
from app.models import Base, Workspace
from tests.factories import create_workspace

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
async def workspace() -> Workspace:
    """A just-added company: discovery hasn't named it yet."""
    return await create_workspace(name=None)


@pytest.fixture
async def api():
    """Client for the unscoped API (`/meta`, `/workspaces`)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test/api/v1") as c:
        yield c


@pytest.fixture
async def client(workspace):
    """Client scoped to the default workspace: paths are relative to `/workspaces/{id}`."""
    base_url = f"http://test/api/v1/workspaces/{workspace.id}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url=base_url) as c:
        yield c


@pytest.fixture
def demo_mode(monkeypatch):
    monkeypatch.setattr(settings, "demo_mode", True)
