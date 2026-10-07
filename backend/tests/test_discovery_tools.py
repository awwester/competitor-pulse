import pytest
from sqlalchemy import select

from app.agent.discovery.tools import build_company_tools, build_page_tools
from app.config import settings
from app.db import SessionLocal
from app.models import Competitor, CompetitorSuggestion, RunKind, TrackedPage, Workspace
from app.services.crawler import PageFetch
from tests.factories import create_competitor, create_run


class FakeCrawler:
    """Serves the given URL -> text; anything else is a 404."""

    def __init__(self, pages: dict[str, str]):
        self.pages = pages

    async def fetch(self, url: str) -> PageFetch:
        if url not in self.pages:
            return PageFetch(url=url, http_status=404, text="Not found")
        return PageFetch(url=url, http_status=200, text=self.pages[url])


def text_of(result) -> str:
    return result["content"][0]["text"]


@pytest.fixture
async def company_tools(workspace):
    run = await create_run(workspace, kind=RunKind.COMPANY_DISCOVERY)
    crawler = FakeCrawler({"https://globex.test": "Globex invoicing", "https://acme.test": "Acme"})
    tools = {t.name: t.handler for t in build_company_tools(run.id, workspace.id, crawler)}
    return run, tools


async def suggestions(run) -> list[CompetitorSuggestion]:
    async with SessionLocal() as session:
        return list(
            (
                await session.scalars(
                    select(CompetitorSuggestion).where(CompetitorSuggestion.run_id == run.id)
                )
            ).all()
        )


async def test_suggest_competitor_records_suggestion(company_tools):
    run, tools = company_tools
    await tools["suggest_competitor"](
        {"name": "Globex", "website": "https://globex.test", "rationale": "Same segment"}
    )
    [suggestion] = await suggestions(run)
    assert (suggestion.name, suggestion.rationale) == ("Globex", "Same segment")


async def test_suggest_competitor_rejects_unreachable_site(company_tools):
    run, tools = company_tools
    result = await tools["suggest_competitor"](
        {"name": "Ghost", "website": "https://ghost.test", "rationale": "?"}
    )
    assert result["is_error"] and await suggestions(run) == []


async def test_suggest_competitor_rejects_tracked_competitor(company_tools, workspace):
    run, tools = company_tools
    await create_competitor(workspace)  # https://acme.test
    result = await tools["suggest_competitor"](
        {"name": "Acme", "website": "https://www.acme.test/", "rationale": "?"}
    )
    assert "already tracked" in text_of(result)


async def test_suggest_competitor_rejects_own_website(company_tools, workspace):
    run, tools = company_tools
    async with SessionLocal() as session:
        (await session.get(Workspace, workspace.id)).website = "https://globex.test"
        await session.commit()
    result = await tools["suggest_competitor"](
        {"name": "Us", "website": "https://globex.test", "rationale": "?"}
    )
    assert "own website" in text_of(result)


async def test_save_profile_fills_empty_profile_and_default_name(company_tools, workspace):
    _, tools = company_tools
    await tools["save_profile"]({"company_name": "Tallybird", "profile": "We are Tallybird."})
    async with SessionLocal() as session:
        saved = await session.get(Workspace, workspace.id)
    assert (saved.name, saved.company_profile) == ("Tallybird", "We are Tallybird.")


async def test_save_profile_keeps_existing_profile(company_tools, workspace):
    _, tools = company_tools
    async with SessionLocal() as session:
        (await session.get(Workspace, workspace.id)).company_profile = "Written by hand."
        await session.commit()
    await tools["save_profile"]({"company_name": "Tallybird", "profile": "Agent draft."})
    async with SessionLocal() as session:
        assert (await session.get(Workspace, workspace.id)).company_profile == "Written by hand."


@pytest.fixture
async def competitor(workspace):
    return await create_competitor(workspace)  # tracks https://acme.test/pricing


def page_tools(competitor, pages: dict[str, str]):
    return {t.name: t.handler for t in build_page_tools(competitor.id, FakeCrawler(pages))}


async def tracked_urls(competitor) -> list[str]:
    async with SessionLocal() as session:
        return list(
            await session.scalars(
                select(TrackedPage.url).where(TrackedPage.competitor_id == competitor.id)
            )
        )


async def test_add_page_tracks_page_with_rationale(competitor):
    tools = page_tools(competitor, {"https://acme.test/changelog": "v2.1 released"})
    await tools["add_page"](
        {"url": "https://acme.test/changelog", "page_type": "changelog", "rationale": "Releases"}
    )
    async with SessionLocal() as session:
        page = await session.scalar(
            select(TrackedPage).where(TrackedPage.url == "https://acme.test/changelog")
        )
    assert page.rationale == "Releases"


async def test_add_page_rejects_other_site(competitor):
    tools = page_tools(competitor, {"https://elsewhere.test/pricing": "Prices"})
    result = await tools["add_page"](
        {"url": "https://elsewhere.test/pricing", "page_type": "pricing", "rationale": "?"}
    )
    assert result["is_error"] and len(await tracked_urls(competitor)) == 1


async def test_add_page_rejects_missing_page(competitor):
    tools = page_tools(competitor, {})
    result = await tools["add_page"](
        {"url": "https://acme.test/careers", "page_type": "careers", "rationale": "?"}
    )
    assert "HTTP 404" in text_of(result)


async def test_add_page_stops_at_max_pages(competitor, monkeypatch):
    monkeypatch.setattr(settings, "discovery_max_pages", 1)
    tools = page_tools(competitor, {"https://acme.test/blog": "Posts"})
    result = await tools["add_page"](
        {"url": "https://acme.test/blog", "page_type": "blog", "rationale": "?"}
    )
    assert "maximum" in text_of(result)


async def test_save_notes_fills_empty_notes(competitor):
    await page_tools(competitor, {})["save_notes"]({"notes": "Invoicing for freelancers."})
    async with SessionLocal() as session:
        assert (await session.get(Competitor, competitor.id)).notes == "Invoicing for freelancers."


async def test_save_notes_keeps_existing_notes(competitor):
    async with SessionLocal() as session:
        (await session.get(Competitor, competitor.id)).notes = "Written by hand."
        await session.commit()
    await page_tools(competitor, {})["save_notes"]({"notes": "Agent draft."})
    async with SessionLocal() as session:
        assert (await session.get(Competitor, competitor.id)).notes == "Written by hand."
