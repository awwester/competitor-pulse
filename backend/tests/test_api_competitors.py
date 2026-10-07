from tests.factories import create_competitor

COMPETITOR = {
    "name": "Ledgerly",
    "website": "https://ledgerly.test",
    "pages": [{"url": "https://ledgerly.test/pricing", "pageType": "pricing"}],
}


async def test_create_competitor_returns_pages_in_camel_case(client, workspace):
    response = await client.post("/api/v1/competitors", json=COMPETITOR)
    assert response.json()["pages"][0]["pageType"] == "pricing"


async def test_create_competitor_rejects_non_http_url(client, workspace):
    response = await client.post("/api/v1/competitors", json={**COMPETITOR, "website": "ftp://x"})
    assert response.status_code == 422


async def test_list_competitors_returns_workspace_competitors(client, workspace):
    await create_competitor(workspace, name="Acme")
    response = await client.get("/api/v1/competitors")
    assert [c["name"] for c in response.json()] == ["Acme"]


async def test_update_competitor_changes_only_given_fields(client, workspace):
    competitor = await create_competitor(workspace)
    response = await client.patch(f"/api/v1/competitors/{competitor.id}", json={"notes": "Watch"})
    assert (response.json()["notes"], response.json()["name"]) == ("Watch", "Acme")


async def test_delete_competitor_removes_it(client, workspace):
    competitor = await create_competitor(workspace)
    await client.delete(f"/api/v1/competitors/{competitor.id}")
    assert (await client.get("/api/v1/competitors")).json() == []


async def test_add_page_attaches_to_competitor(client, workspace):
    competitor = await create_competitor(workspace, page_urls=())
    response = await client.post(
        f"/api/v1/competitors/{competitor.id}/pages", json={"url": "https://acme.test/changelog"}
    )
    assert response.json()["competitorId"] == str(competitor.id)


async def test_update_page_toggles_active(client, workspace):
    competitor = await create_competitor(workspace)
    response = await client.patch(
        f"/api/v1/pages/{competitor.pages[0].id}", json={"isActive": False}
    )
    assert response.json()["isActive"] is False


async def test_demo_mode_blocks_writes(client, workspace, demo_mode):
    response = await client.post("/api/v1/competitors", json=COMPETITOR)
    assert response.status_code == 403
