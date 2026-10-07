import pytest

from app.models import RunEventKind, RunStatus
from app.services.run_log import RunLog
from tests.factories import create_changed_page, create_finding, create_run


@pytest.fixture
def delivered(monkeypatch):
    calls = []

    async def fake_deliver(workspace, digest):
        calls.append(digest)
        return ["Slack"], []

    monkeypatch.setattr("app.api.runs.deliver", fake_deliver)
    return calls


async def test_create_run_queues_it(client, workspace):
    response = await client.post("/api/v1/runs")
    assert response.json()["status"] == "queued"


async def test_create_run_conflicts_while_one_is_active(client, workspace):
    await create_run(workspace, RunStatus.RUNNING)
    response = await client.post("/api/v1/runs")
    assert response.status_code == 409


async def test_get_run_includes_findings(client, workspace):
    changed = await create_changed_page(workspace, "Pro $35", "Pro $29")
    await create_finding(changed)
    response = await client.get(f"/api/v1/runs/{changed.run.id}")
    assert response.json()["findings"][0]["competitorName"] == "Acme"


async def test_list_events_returns_only_events_after_seq(client, workspace):
    run = await create_run(workspace)
    log = RunLog(run.id)
    for title in ("one", "two", "three"):
        await log.phase(title)
    response = await client.get(f"/api/v1/runs/{run.id}/events", params={"after": 0})
    assert [e["payload"]["title"] for e in response.json()] == ["two", "three"]


async def test_publish_requires_awaiting_review(client, workspace, delivered):
    run = await create_run(workspace, RunStatus.RUNNING)
    response = await client.post(f"/api/v1/runs/{run.id}/publish")
    assert response.status_code == 409


async def test_publish_marks_run_published(client, workspace, delivered):
    run = await create_run(workspace, RunStatus.AWAITING_REVIEW)
    response = await client.post(f"/api/v1/runs/{run.id}/publish")
    assert response.json()["status"] == "published"


async def test_publish_excludes_dismissed_findings_from_digest(client, workspace, delivered):
    changed = await create_changed_page(workspace, "a", "b", status=RunStatus.AWAITING_REVIEW)
    await create_finding(changed, title="Kept")
    await create_finding(changed, title="Dropped", is_dismissed=True)
    await client.post(f"/api/v1/runs/{changed.run.id}/publish")
    assert "Dropped" not in delivered[0].body


async def test_publish_logs_published_phase(client, workspace, delivered):
    run = await create_run(workspace, RunStatus.AWAITING_REVIEW)
    await client.post(f"/api/v1/runs/{run.id}/publish")
    events = (await client.get(f"/api/v1/runs/{run.id}/events")).json()
    assert (
        events[-1]["kind"] == RunEventKind.PHASE and events[-1]["payload"]["title"] == "Published"
    )


async def test_dismiss_marks_run_dismissed(client, workspace):
    run = await create_run(workspace, RunStatus.AWAITING_REVIEW)
    response = await client.post(f"/api/v1/runs/{run.id}/dismiss")
    assert response.json()["status"] == "dismissed"


async def test_update_finding_dismisses_it(client, workspace):
    finding = await create_finding(await create_changed_page(workspace, "a", "b"))
    response = await client.patch(f"/api/v1/findings/{finding.id}", json={"isDismissed": True})
    assert response.json()["isDismissed"] is True


async def test_dashboard_reports_total_cost(client, workspace):
    await create_run(workspace, RunStatus.PUBLISHED, cost_usd=0.42)
    response = await client.get("/api/v1/dashboard")
    assert response.json()["totalCostUsd"] == pytest.approx(0.42)
