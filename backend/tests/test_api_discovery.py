from sqlalchemy import select

from app.db import SessionLocal
from app.models import Competitor, CompetitorSuggestion, Run, RunKind, RunStatus
from tests.factories import create_run


async def create_review(workspace, *suggestions: tuple[str, str, bool]) -> Run:
    """A company discovery awaiting review with (name, website, is_selected) suggestions."""
    run = await create_run(workspace, RunStatus.AWAITING_REVIEW, kind=RunKind.COMPANY_DISCOVERY)
    async with SessionLocal() as session:
        session.add_all(
            CompetitorSuggestion(run_id=run.id, name=name, website=website, is_selected=selected)
            for name, website, selected in suggestions
        )
        await session.commit()
    return run


async def queued_kinds() -> list[RunKind]:
    async with SessionLocal() as session:
        return list(
            await session.scalars(
                select(Run.kind).where(Run.status == RunStatus.QUEUED).order_by(Run.kind)
            )
        )


async def test_start_discovery_saves_website_and_queues_it(client, workspace):
    response = await client.post("/api/v1/discovery", json={"website": "https://tallybird.test"})
    assert response.json()["kind"] == "company_discovery"
    workspace_body = (await client.get("/api/v1/workspace")).json()
    assert workspace_body["website"] == "https://tallybird.test"


async def test_start_discovery_conflicts_while_one_is_active(client, workspace):
    await client.post("/api/v1/discovery", json={"website": "https://tallybird.test"})
    response = await client.post("/api/v1/discovery", json={"website": "https://tallybird.test"})
    assert response.status_code == 409


async def test_apply_tracks_only_selected_suggestions(client, workspace):
    run = await create_review(
        workspace,
        ("Globex", "https://globex.test", True),
        ("Initech", "https://initech.test", False),
    )
    await client.post(f"/api/v1/runs/{run.id}/apply")
    async with SessionLocal() as session:
        assert list(await session.scalars(select(Competitor.name))) == ["Globex"]


async def test_apply_queues_page_discovery_per_competitor_and_a_check(client, workspace):
    run = await create_review(
        workspace,
        ("Globex", "https://globex.test", True),
        ("Initech", "https://initech.test", True),
    )
    await client.post(f"/api/v1/runs/{run.id}/apply")
    assert await queued_kinds() == [RunKind.CHECK, RunKind.PAGE_DISCOVERY, RunKind.PAGE_DISCOVERY]


async def test_apply_queues_check_after_page_discoveries(client, workspace):
    run = await create_review(workspace, ("Globex", "https://globex.test", True))
    await client.post(f"/api/v1/runs/{run.id}/apply")
    async with SessionLocal() as session:
        created = dict(
            (await session.execute(select(Run.kind, Run.created_at).where(Run.id != run.id))).all()
        )
    assert created[RunKind.CHECK] > created[RunKind.PAGE_DISCOVERY]


async def test_apply_marks_run_applied(client, workspace):
    run = await create_review(workspace, ("Globex", "https://globex.test", True))
    response = await client.post(f"/api/v1/runs/{run.id}/apply")
    assert response.json()["status"] == "applied"


async def test_apply_rejects_check_run(client, workspace):
    run = await create_run(workspace, RunStatus.AWAITING_REVIEW)
    response = await client.post(f"/api/v1/runs/{run.id}/apply")
    assert response.status_code == 409


async def test_publish_rejects_discovery_run(client, workspace):
    run = await create_review(workspace)
    response = await client.post(f"/api/v1/runs/{run.id}/publish")
    assert response.status_code == 409


async def test_add_suggestion_appears_on_run(client, workspace):
    run = await create_review(workspace)
    await client.post(
        f"/api/v1/runs/{run.id}/suggestions",
        json={"name": "Hooli", "website": "https://hooli.test"},
    )
    detail = (await client.get(f"/api/v1/runs/{run.id}")).json()
    assert [s["name"] for s in detail["suggestions"]] == ["Hooli"]


async def test_update_suggestion_deselects_it(client, workspace):
    run = await create_review(workspace, ("Globex", "https://globex.test", True))
    suggestion_id = (await client.get(f"/api/v1/runs/{run.id}")).json()["suggestions"][0]["id"]
    response = await client.patch(
        f"/api/v1/suggestions/{suggestion_id}", json={"isSelected": False}
    )
    assert response.json()["isSelected"] is False


async def test_create_competitor_without_pages_queues_page_discovery(client, workspace):
    await client.post(
        "/api/v1/competitors", json={"name": "Globex", "website": "https://globex.test"}
    )
    assert await queued_kinds() == [RunKind.PAGE_DISCOVERY]


async def test_create_competitor_with_pages_skips_page_discovery(client, workspace):
    await client.post(
        "/api/v1/competitors",
        json={
            "name": "Globex",
            "website": "https://globex.test",
            "pages": [{"url": "https://globex.test/pricing", "pageType": "pricing"}],
        },
    )
    assert await queued_kinds() == []


async def test_discover_pages_queues_page_discovery_for_competitor(client, workspace):
    created = await client.post(
        "/api/v1/competitors",
        json={
            "name": "Globex",
            "website": "https://globex.test",
            "pages": [{"url": "https://globex.test/pricing", "pageType": "pricing"}],
        },
    )
    response = await client.post(f"/api/v1/competitors/{created.json()['id']}/discover")
    assert response.json()["competitorId"] == created.json()["id"]
