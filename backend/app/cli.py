"""Management commands. Usage: python -m app.cli <command>"""

import argparse
import asyncio

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Competitor, PageType, RunTrigger, TrackedPage, Workspace
from app.services.runs import enqueue_checks

DEMO_SITES_URL = "http://demo-sites"
DEMO_WEBSITE = f"{DEMO_SITES_URL}/tallybird/"

DEMO_PROFILE = """\
We are Tallybird, invoicing and payments software for freelancers and small creative studios \
(1-10 people), mostly in the US and UK.

Plans: Solo $12/mo (up to 5 clients), Studio $29/mo (unlimited clients, 3 seats), Agency $79/mo \
(10 seats, client portal). 14-day free trial, no free tier.

What we win on: automatic late-payment reminders, the fastest invoice creation flow on the \
market, and pricing that's cheaper than the big players. Weak spots: single-currency only, no \
time tracking, no SOC 2 yet.

We care most about competitors changing price, adding payment reminders or multi-currency, or \
moving into (or out of) the freelancer segment."""

DEMO_COMPETITORS = [
    (
        "Ledgerly",
        f"{DEMO_SITES_URL}/ledgerly/",
        "Closest head-to-head competitor on price.",
        [
            ("ledgerly/pricing.html", PageType.PRICING),
            ("ledgerly/changelog.html", PageType.CHANGELOG),
        ],
    ),
    (
        "Paperplane Billing",
        f"{DEMO_SITES_URL}/paperplane/",
        "Freelancer-focused; strong on time tracking.",
        [
            ("paperplane/index.html", PageType.HOMEPAGE),
            ("paperplane/careers.html", PageType.CAREERS),
        ],
    ),
]


async def seed_demo() -> None:
    async with SessionLocal() as session:
        if await session.scalar(select(Workspace.id).where(Workspace.website == DEMO_WEBSITE)):
            print("Tallybird is already seeded; skipping.")
            return
        workspace = Workspace(
            name="Tallybird", website=DEMO_WEBSITE, company_profile=DEMO_PROFILE, notify_emails=[]
        )
        session.add(workspace)
        await session.flush()
        for name, website, notes, pages in DEMO_COMPETITORS:
            session.add(
                Competitor(
                    workspace_id=workspace.id,
                    name=name,
                    website=website,
                    notes=notes,
                    pages=[
                        TrackedPage(url=f"{DEMO_SITES_URL}/{path}", page_type=page_type)
                        for path, page_type in pages
                    ],
                )
            )
        await session.commit()
    print(f"Seeded Tallybird with {len(DEMO_COMPETITORS)} demo competitors.")


async def run_checks() -> None:
    async with SessionLocal() as session:
        runs = await enqueue_checks(session, RunTrigger.MANUAL)
    print(f"Queued {len(runs)} check{'' if len(runs) == 1 else 's'}.")


COMMANDS = {"seed-demo": seed_demo, "run-checks": run_checks}


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    parser.add_argument("command", choices=COMMANDS)
    asyncio.run(COMMANDS[parser.parse_args().command]())


if __name__ == "__main__":
    main()
