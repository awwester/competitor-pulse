WEBHOOK = "https://hooks.slack.com/services/T000/B000/secret"


async def test_slack_webhook_is_saved_but_never_returned(client, workspace):
    response = await client.patch("/api/v1/workspace", json={"slackWebhookUrl": WEBHOOK})
    fetched = await client.get("/api/v1/workspace")

    assert response.json()["slackConfigured"] is True
    assert WEBHOOK not in response.text + fetched.text
