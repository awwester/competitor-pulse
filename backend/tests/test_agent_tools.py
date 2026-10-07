import json
import uuid

import pytest
from sqlalchemy import select

from app.agent.tools import build_tools
from app.db import SessionLocal
from app.models import Finding, Run
from tests.factories import create_changed_page


@pytest.fixture
async def changed(workspace):
    return await create_changed_page(workspace, "Starter\n$15 / month", "Free\n$0 / month")


def tools_for(run_id):
    return {t.name: t.handler for t in build_tools(run_id)}


def text_of(result) -> str:
    return result["content"][0]["text"]


async def test_list_changed_pages_includes_change_stats(changed):
    result = await tools_for(changed.run.id)["list_changed_pages"]({})
    [page] = json.loads(text_of(result))
    assert (page["tracked_page_id"], page["lines_added"]) == (str(changed.page.id), 2)


async def test_get_page_diff_shows_added_lines(changed):
    result = await tools_for(changed.run.id)["get_page_diff"](
        {"tracked_page_id": str(changed.page.id)}
    )
    assert "+$0 / month" in text_of(result)


async def test_get_page_diff_rejects_page_outside_run(changed):
    result = await tools_for(uuid.uuid4())["get_page_diff"](
        {"tracked_page_id": str(changed.page.id)}
    )
    assert result["is_error"] is True


async def test_record_finding_persists_finding(changed):
    await tools_for(changed.run.id)["record_finding"](
        {
            "tracked_page_id": str(changed.page.id),
            "category": "pricing",
            "significance": 5,
            "title": "New free tier",
            "summary": "Starter replaced by a free plan.",
            "evidence": "Free $0 / month",
        }
    )
    async with SessionLocal() as session:
        finding = await session.scalar(select(Finding))
    assert finding.title == "New free tier"


async def test_record_finding_rejects_out_of_range_significance(changed):
    result = await tools_for(changed.run.id)["record_finding"](
        {
            "tracked_page_id": str(changed.page.id),
            "category": "pricing",
            "significance": 9,
            "title": "x",
            "summary": "x",
            "evidence": "x",
        }
    )
    assert result["is_error"] is True


async def test_submit_report_saves_headline_and_report(changed):
    await tools_for(changed.run.id)["submit_report"](
        {"headline": "Ledgerly went free", "report_markdown": "## Takeaways"}
    )
    async with SessionLocal() as session:
        run = await session.get(Run, changed.run.id)
    assert (run.headline, run.report_markdown) == ("Ledgerly went free", "## Takeaways")
