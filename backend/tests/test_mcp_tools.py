from mcp.client import Client
from sqlalchemy import select

from app.db import SessionLocal
from app.mcp_server import mcp
from app.models import FindingCategory, Run, RunKind, RunStatus
from tests.factories import (
    create_changed_page,
    create_competitor,
    create_finding,
    create_run,
    create_workspace,
)


async def call(tool: str, arguments: dict):
    """One tool call through an in-process MCP client. (A client fixture can't be used: its task
    group must exit in the task that entered it.)"""
    async with Client(mcp) as client:
        return await client.call_tool(tool, arguments)


def result_of(response):
    assert not response.is_error, response.content
    return response.structured_content["result"]


async def test_only_reads_and_safe_actions_are_exposed():
    """Publishing a digest and approving discovered competitors stay with a person in the UI."""
    async with Client(mcp) as client:
        names = {tool.name for tool in (await client.list_tools()).tools}
    assert names == {
        "list_workspaces",
        "list_competitors",
        "search_findings",
        "list_runs",
        "get_run",
        "queue_check",
        "add_competitor",
        "remove_competitor",
        "add_page",
        "remove_page",
        "set_finding_dismissed",
    }


async def test_list_workspaces_returns_every_company(workspace):
    await create_workspace("Globex")
    response = await call("list_workspaces", {})
    assert len(result_of(response)) == 2


async def test_search_findings_filters_by_category_and_significance(workspace):
    changed = await create_changed_page(workspace, "Pro $35", "Pro $29")
    await create_finding(changed, title="Price cut", significance=4)
    await create_finding(changed, title="Minor price tweak", significance=2)
    await create_finding(changed, title="New hire", category=FindingCategory.HIRING)
    response = await call(
        "search_findings",
        {"workspace_id": str(workspace.id), "category": "pricing", "min_significance": 3},
    )
    assert [f["title"] for f in result_of(response)] == ["Price cut"]


async def test_search_findings_leaves_out_dismissed(workspace):
    changed = await create_changed_page(workspace, "Pro $35", "Pro $29")
    await create_finding(changed, is_dismissed=True)
    response = await call("search_findings", {"workspace_id": str(workspace.id)})
    assert result_of(response) == []


async def test_run_from_another_workspace_is_a_tool_error(workspace):
    run = await create_run(await create_workspace("Globex"))
    response = await call("get_run", {"workspace_id": str(workspace.id), "run_id": str(run.id)})
    assert response.is_error
    assert "Run not found" in response.content[0].text


async def test_queue_check_conflicts_while_one_is_active(workspace):
    await create_run(workspace, RunStatus.RUNNING)
    response = await call("queue_check", {"workspace_id": str(workspace.id)})
    assert "already queued or in progress" in response.content[0].text


async def test_add_competitor_without_pages_queues_page_discovery(workspace):
    await call(
        "add_competitor",
        {
            "workspace_id": str(workspace.id),
            "competitor": {"name": "Ledgerly", "website": "https://ledgerly.test"},
        },
    )
    async with SessionLocal() as session:
        kinds = (await session.scalars(select(Run.kind))).all()
    assert kinds == [RunKind.PAGE_DISCOVERY]


async def test_write_tools_fail_in_demo_mode(workspace, demo_mode):
    competitor = await create_competitor(workspace)
    response = await call(
        "remove_competitor",
        {"workspace_id": str(workspace.id), "competitor_id": str(competitor.id)},
    )
    assert "read-only demo" in response.content[0].text
