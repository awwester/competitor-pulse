"""Agent evals: run the real analyst on fixed before/after page pairs and check its findings.

Unlike the unit tests, this calls the Claude API and costs money (typically well under $1 for
the full suite). Run with `make eval`.
"""

import asyncio
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select

from app.agent.analyst import analyze_run
from app.cli import DEMO_PROFILE
from app.config import settings
from app.db import SessionLocal, engine
from app.models import Base, Finding, PageType, Run, RunStatus, Workspace
from app.services.run_log import RunLog
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


async def run_case(workspace: Workspace, name: str, case: dict) -> CaseResult:
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
    if outcome.error:
        failures.insert(0, f"agent error: {outcome.error}")
    if not has_report:
        failures.append("agent did not submit a report")
    return CaseResult(
        name=name,
        passed=not failures,
        failures=failures,
        findings=[
            {"category": f.category.value, "significance": f.significance, "title": f.title}
            for f in findings
        ],
        cost_usd=outcome.usage.cost_usd,
        num_turns=outcome.usage.num_turns,
    )


async def main(selected: list[str]) -> int:
    assert settings.database_url.endswith("_test"), "Evals must run against the *_test database"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        workspace = Workspace(name="Tallybird", company_profile=DEMO_PROFILE, notify_emails=[])
        session.add(workspace)
        await session.commit()

    paths = sorted(CASES_DIR.glob("*.json"))
    if selected:
        paths = [p for p in paths if p.stem in selected]

    results = []
    for path in paths:
        result = await run_case(workspace, path.stem, json.loads(path.read_text()))
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(f"{status}  {result.name:<20} ${result.cost_usd:.3f}  {result.num_turns} turns")
        for failure in result.failures:
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
