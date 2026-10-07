import pytest

from app.agent.runner import AgentOutcome
from app.agent.tracing import Usage
from app.db import SessionLocal
from app.models import Run, RunKind, RunStatus, TrackedPage
from app.services.crawler import PageFetch
from app.worker import check, discovery, pipeline
from tests.factories import create_competitor, create_run, create_snapshot


@pytest.fixture
def page_text(monkeypatch):
    """Maps URL -> text the fake crawler returns. Mutate it between runs to simulate changes.

    Text starting with "404" is served with that status code.
    """
    pages: dict[str, str] = {}

    class FakeCrawler:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return None

        async def fetch(self, url: str) -> PageFetch:
            status = 404 if pages[url].startswith("404") else 200
            return PageFetch(url=url, http_status=status, text=pages[url])

    monkeypatch.setattr(check, "Crawler", FakeCrawler)
    return pages


@pytest.fixture
def analyst(monkeypatch):
    """Fake analyst that writes a report and reports usage, like the real agent would."""
    calls = []

    async def fake_analyze(workspace, run_id, pages_changed, log):
        calls.append(pages_changed)
        async with SessionLocal() as session:
            (await session.get(Run, run_id)).report_markdown = "## Report"
            await session.commit()
        return AgentOutcome(usage=Usage(num_turns=3, cost_usd=0.12), error=None)

    monkeypatch.setattr(check, "analyze_run", fake_analyze)
    return calls


async def get_run(run_id) -> Run:
    async with SessionLocal() as session:
        return await session.get(Run, run_id)


async def test_first_capture_is_baseline_not_change(workspace, page_text, analyst):
    competitor = await create_competitor(workspace)
    page_text[competitor.pages[0].url] = "Pro $35"
    run = await create_run(workspace, RunStatus.RUNNING)
    await pipeline.execute_run(run.id)
    assert (await get_run(run.id)).status == RunStatus.NO_CHANGES


async def test_unchanged_page_skips_agent(workspace, page_text, analyst):
    competitor = await create_competitor(workspace)
    await create_snapshot(competitor.pages[0], "Pro $35")
    page_text[competitor.pages[0].url] = "Pro $35"
    run = await create_run(workspace, RunStatus.RUNNING)
    await pipeline.execute_run(run.id)
    assert analyst == []


async def test_error_page_is_not_treated_as_change(workspace, page_text, analyst):
    competitor = await create_competitor(workspace)
    await create_snapshot(competitor.pages[0], "Pro $35")
    page_text[competitor.pages[0].url] = "404 Not Found"
    run = await create_run(workspace, RunStatus.RUNNING)
    await pipeline.execute_run(run.id)
    assert analyst == []


async def test_changed_page_runs_agent_and_awaits_review(workspace, page_text, analyst):
    competitor = await create_competitor(workspace)
    await create_snapshot(competitor.pages[0], "Pro $35")
    page_text[competitor.pages[0].url] = "Pro $29"
    run = await create_run(workspace, RunStatus.RUNNING)
    await pipeline.execute_run(run.id)
    finished = await get_run(run.id)
    assert (finished.status, finished.pages_changed, finished.cost_usd) == (
        RunStatus.AWAITING_REVIEW,
        1,
        0.12,
    )


async def test_agent_without_report_fails_run(workspace, page_text, monkeypatch):
    async def no_report(workspace, run_id, pages_changed, log):
        return AgentOutcome(usage=Usage(), error=None)

    monkeypatch.setattr(check, "analyze_run", no_report)
    competitor = await create_competitor(workspace)
    await create_snapshot(competitor.pages[0], "Pro $35")
    page_text[competitor.pages[0].url] = "Pro $29"
    run = await create_run(workspace, RunStatus.RUNNING)
    await pipeline.execute_run(run.id)
    assert (await get_run(run.id)).status == RunStatus.FAILED


async def test_company_discovery_with_summary_awaits_review(workspace, monkeypatch):
    async def fake_discover(workspace, run_id, log):
        async with SessionLocal() as session:
            (await session.get(Run, run_id)).headline = "Found 3 competitors"
            await session.commit()
        return AgentOutcome(usage=Usage(cost_usd=0.3), error=None)

    monkeypatch.setattr(discovery, "discover_company", fake_discover)
    run = await create_run(workspace, RunStatus.RUNNING, kind=RunKind.COMPANY_DISCOVERY)
    await pipeline.execute_run(run.id)
    assert (await get_run(run.id)).status == RunStatus.AWAITING_REVIEW


async def test_company_discovery_without_summary_fails(workspace, monkeypatch):
    async def fake_discover(workspace, run_id, log):
        return AgentOutcome(usage=Usage(), error=None)

    monkeypatch.setattr(discovery, "discover_company", fake_discover)
    run = await create_run(workspace, RunStatus.RUNNING, kind=RunKind.COMPANY_DISCOVERY)
    await pipeline.execute_run(run.id)
    assert (await get_run(run.id)).status == RunStatus.FAILED


async def test_page_discovery_completes_with_count_of_pages_added(workspace, monkeypatch):
    async def fake_discover(competitor, log):
        async with SessionLocal() as session:
            session.add(TrackedPage(competitor_id=competitor.id, url="https://acme.test/changelog"))
            await session.commit()
        return AgentOutcome(usage=Usage(), error=None)

    monkeypatch.setattr(discovery, "discover_pages", fake_discover)
    competitor = await create_competitor(workspace)
    run = await create_run(
        workspace, RunStatus.RUNNING, kind=RunKind.PAGE_DISCOVERY, competitor_id=competitor.id
    )
    await pipeline.execute_run(run.id)
    finished = await get_run(run.id)
    assert (finished.status, finished.headline) == (RunStatus.COMPLETED, "Added 1 page for Acme")


async def test_page_discovery_agent_error_fails_run(workspace, monkeypatch):
    async def fake_discover(competitor, log):
        return AgentOutcome(usage=Usage(), error="Budget exceeded")

    monkeypatch.setattr(discovery, "discover_pages", fake_discover)
    competitor = await create_competitor(workspace)
    run = await create_run(
        workspace, RunStatus.RUNNING, kind=RunKind.PAGE_DISCOVERY, competitor_id=competitor.id
    )
    await pipeline.execute_run(run.id)
    assert (await get_run(run.id)).error == "Budget exceeded"
