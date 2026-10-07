"""Agent evals: run the real agents and check what they produce.

- Analyst: fixed before/after page pairs (cases/*.json) → expected findings.
- Discovery: the demo sites (needs the demo-sites service) → expected competitors and pages.

Unlike the unit tests, this calls the Claude API and costs money (typically around $1 for the
full suite). Run with `make eval`, or `make eval cases="pricing_cut discover_company"`.
"""

import asyncio
import json
import sys
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select

from app.agent.analyst import analyze_run
from app.agent.discovery import discover_company, discover_pages
from app.agent.runner import AgentOutcome
from app.cli import DEMO_PROFILE, DEMO_SITES_URL
from app.config import settings
from app.db import SessionLocal, engine
from app.models import (
    Base,
    Competitor,
    CompetitorSuggestion,
    Finding,
    PageType,
    Run,
    RunKind,
    RunStatus,
    TrackedPage,
    Workspace,
)
from app.services.run_log import RunLog
from app.services.urls import site_key
from tests.factories import create_competitor, create_run, create_snapshot

CASES_DIR = Path(__file__).parent / "cases"
RESULTS_DIR = Path(__file__).parent / "results"


@dataclass
class CaseResult:
    name: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)
    cost_usd: float = 0.0
    num_turns: int = 0


Case = Callable[[str], Awaitable[CaseResult]]


def check(expect: dict, findings: list[Finding]) -> list[str]:
    failures = []
    top = max((f.significance for f in findings), default=0)
    categories = {f.category.value for f in findings}
    if len(findings) < expect.get("min_findings", 0):
        failures.append(f"expected ≥{expect['min_findings']} findings, got {len(findings)}")
    if "max_findings" in expect and len(findings) > expect["max_findings"]:
        failures.append(f"expected ≤{expect['max_findings']} findings, got {len(findings)}")
    if "categories_any" in expect and not categories & set(expect["categories_any"]):
        failures.append(
            f"expected a category in {expect['categories_any']}, got {sorted(categories)}"
        )
    if top < expect.get("min_top_significance", 0):
        failures.append(f"expected top significance ≥{expect['min_top_significance']}, got {top}")
    if top > expect.get("max_top_significance", 5):
        failures.append(f"expected top significance ≤{expect['max_top_significance']}, got {top}")
    return failures


def result(name: str, outcome: AgentOutcome, failures: list[str], **details) -> CaseResult:
    if outcome.error:
        failures.insert(0, f"agent error: {outcome.error}")
    return CaseResult(
        name=name,
        passed=not failures,
        failures=failures,
        cost_usd=outcome.usage.cost_usd,
        num_turns=outcome.usage.num_turns,
        **details,
    )


async def create_workspace(**fields) -> Workspace:
    async with SessionLocal() as session:
        workspace = Workspace(name="Tallybird", notify_emails=[], **fields)
        session.add(workspace)
        await session.commit()
        return workspace


async def run_analyst_case(name: str) -> CaseResult:
    case = json.loads((CASES_DIR / f"{name}.json").read_text())
    workspace = await create_workspace(company_profile=DEMO_PROFILE)
    competitor = await create_competitor(
        workspace,
        name=case["competitor"],
        page_urls=(f"https://{name}.example/{case['page_type']}",),
        page_type=PageType(case["page_type"]),
    )
    page = competitor.pages[0]
    baseline = await create_snapshot(page, case["before"])
    run = await create_run(workspace, RunStatus.RUNNING)
    await create_snapshot(page, case["after"], run=run, previous=baseline)

    outcome = await analyze_run(workspace, run.id, 1, RunLog(run.id))
    async with SessionLocal() as session:
        findings = list(
            (await session.scalars(select(Finding).where(Finding.run_id == run.id))).all()
        )
        has_report = bool((await session.get(Run, run.id)).report_markdown)

    failures = check(case["expect"], findings)
    if not has_report:
        failures.append("agent did not submit a report")
    return result(
        name,
        outcome,
        failures,
        findings=[
            {"category": f.category.value, "significance": f.significance, "title": f.title}
            for f in findings
        ],
    )


async def discover_company_case(name: str) -> CaseResult:
    """From the Tallybird site alone: write a profile and find both demo competitors."""
    workspace = await create_workspace(website=f"{DEMO_SITES_URL}/tallybird/")
    run = await create_run(workspace, RunStatus.RUNNING, kind=RunKind.COMPANY_DISCOVERY)
    outcome = await discover_company(workspace, run.id, RunLog(run.id))
    async with SessionLocal() as session:
        suggested = {
            site_key(s.website)
            for s in await session.scalars(
                select(CompetitorSuggestion).where(CompetitorSuggestion.run_id == run.id)
            )
        }
        profile = (await session.get(Workspace, workspace.id)).company_profile
        headline = (await session.get(Run, run.id)).headline

    failures = [
        f"missed {competitor}"
        for competitor in ("ledgerly", "paperplane")
        if site_key(f"{DEMO_SITES_URL}/{competitor}/") not in suggested
    ]
    if not profile:
        failures.append("no profile saved")
    if not headline:
        failures.append("no summary submitted")
    return result(name, outcome, failures, findings=[{"suggested": sorted(suggested)}])


async def discover_pages_case(name: str) -> CaseResult:
    """Ledgerly's homepage alone: find its pricing and changelog pages and write notes."""
    workspace = await create_workspace()
    async with SessionLocal() as session:
        competitor = Competitor(
            workspace_id=workspace.id, name="Ledgerly", website=f"{DEMO_SITES_URL}/ledgerly/"
        )
        session.add(competitor)
        await session.commit()
    run = await create_run(
        workspace, RunStatus.RUNNING, kind=RunKind.PAGE_DISCOVERY, competitor_id=competitor.id
    )
    outcome = await discover_pages(competitor, RunLog(run.id))
    async with SessionLocal() as session:
        pages = list(
            await session.scalars(
                select(TrackedPage).where(TrackedPage.competitor_id == competitor.id)
            )
        )
        notes = (await session.get(Competitor, competitor.id)).notes

    tracked = {page.page_type for page in pages}
    failures = [
        f"no {page_type} page"
        for page_type in (PageType.PRICING, PageType.CHANGELOG)
        if page_type not in tracked
    ]
    if not notes:
        failures.append("no notes saved")
    return result(
        name, outcome, failures, findings=[{"page_type": p.page_type, "url": p.url} for p in pages]
    )


DISCOVERY_CASES: dict[str, Case] = {
    "discover_company": discover_company_case,
    "discover_pages": discover_pages_case,
}


async def main(selected: list[str]) -> int:
    assert settings.database_url.endswith("_test"), "Evals must run against the *_test database"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    analyst_cases = {path.stem: run_analyst_case for path in sorted(CASES_DIR.glob("*.json"))}
    cases: dict[str, Case] = analyst_cases | DISCOVERY_CASES
    if selected:
        cases = {name: run for name, run in cases.items() if name in selected}

    results = []
    for name, run_case in cases.items():
        case_result = await run_case(name)
        results.append(case_result)
        status = "PASS" if case_result.passed else "FAIL"
        print(
            f"{status}  {case_result.name:<20} ${case_result.cost_usd:.3f}  "
            f"{case_result.num_turns} turns"
        )
        for failure in case_result.failures:
            print(f"      - {failure}")

    passed = sum(r.passed for r in results)
    total_cost = sum(r.cost_usd for r in results)
    print(f"\n{passed}/{len(results)} passed · ${total_cost:.2f} · model {settings.agent_model}")

    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    (RESULTS_DIR / f"{stamp}.json").write_text(
        json.dumps(
            {
                "model": settings.agent_model,
                "effort": settings.agent_effort,
                "results": [asdict(r) for r in results],
            },
            indent=2,
        )
    )
    await engine.dispose()
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
