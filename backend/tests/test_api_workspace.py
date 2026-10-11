import uuid

from app.db import SessionLocal
from app.models import Competitor, RunStatus
from tests.factories import create_competitor, create_run, create_workspace

WEBHOOK = "https://hooks.slack.com/services/T000/B000/secret"


async def test_slack_webhook_is_saved_but_never_returned(api, workspace):
    response = await api.patch(f"/workspaces/{workspace.id}", json={"slackWebhookUrl": WEBHOOK})
    fetched = await api.get(f"/workspaces/{workspace.id}")

    assert response.json()["slackConfigured"] is True
    assert WEBHOOK not in response.text + fetched.text


async def test_list_workspaces_returns_oldest_first(api, workspace):
    other = await create_workspace()
    response = await api.get("/workspaces")
    assert [w["id"] for w in response.json()] == [str(workspace.id), str(other.id)]


async def test_create_workspace_adds_it_to_the_list(api, workspace):
    response = await api.post(
        "/workspaces", json={"name": "Globex", "website": "https://globex.test"}
    )
    listed = (await api.get("/workspaces")).json()
    assert response.status_code == 201
    assert response.json()["id"] in [w["id"] for w in listed]


async def test_unknown_workspace_is_404(api):
    response = await api.get(f"/workspaces/{uuid.uuid4()}/competitors")
    assert response.status_code == 404


async def test_run_from_another_workspace_is_404(client, workspace):
    run = await create_run(await create_workspace())
    response = await client.get(f"/runs/{run.id}")
    assert response.status_code == 404


async def test_delete_workspace_removes_its_competitors(api, workspace):
    other = await create_workspace()
    competitor = await create_competitor(other)
    response = await api.delete(f"/workspaces/{other.id}")
    async with SessionLocal() as session:
        assert await session.get(Competitor, competitor.id) is None
    assert response.status_code == 204


async def test_cannot_delete_only_workspace(api, workspace):
    response = await api.delete(f"/workspaces/{workspace.id}")
    assert response.status_code == 409


async def test_cannot_delete_workspace_with_active_run(api, workspace):
    other = await create_workspace()
    await create_run(other, RunStatus.RUNNING)
    response = await api.delete(f"/workspaces/{other.id}")
    assert response.status_code == 409
