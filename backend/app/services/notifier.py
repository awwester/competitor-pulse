from dataclasses import dataclass
from email.message import EmailMessage

import aiosmtplib
import httpx

from app.config import settings
from app.models import Finding, Run, Workspace


@dataclass(frozen=True)
class Digest:
    subject: str
    body: str


def build_digest(run: Run, findings: list[Finding]) -> Digest:
    lines = [run.headline or "Competitor update", ""]
    for finding in findings:
        lines.append(
            f"• [{finding.significance}/5 · {finding.category}] "
            f"{finding.competitor_name}: {finding.title}"
        )
        lines.append(f"  {finding.summary}")
        if finding.recommended_action:
            lines.append(f"  → {finding.recommended_action}")
        lines.append("")
    lines.append(f"Full report: {settings.app_url}/runs/{run.id}")
    return Digest(
        subject=f"Competitor Pulse: {run.headline or f'{len(findings)} new findings'}",
        body="\n".join(lines),
    )


async def send_slack(webhook_url: str, digest: Digest) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(webhook_url, json={"text": digest.body})
        response.raise_for_status()


async def send_email(recipients: list[str], digest: Digest) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = ", ".join(recipients)
    message["Subject"] = digest.subject
    message.set_content(digest.body)
    await aiosmtplib.send(message, hostname=settings.smtp_host, port=settings.smtp_port)


async def deliver(workspace: Workspace, digest: Digest) -> tuple[list[str], list[str]]:
    """Send the digest to every configured channel. Returns (delivered, errors)."""
    delivered: list[str] = []
    errors: list[str] = []
    if workspace.slack_webhook_url:
        try:
            await send_slack(workspace.slack_webhook_url, digest)
            delivered.append("Slack")
        except httpx.HTTPError as exc:
            errors.append(f"Slack delivery failed: {exc}")
    if workspace.notify_emails and settings.smtp_host:
        try:
            await send_email(workspace.notify_emails, digest)
            delivered.append(f"email ({len(workspace.notify_emails)})")
        except (aiosmtplib.SMTPException, OSError) as exc:
            errors.append(f"Email delivery failed: {exc}")
    return delivered, errors
