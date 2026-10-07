import pytest

from app.db import SessionLocal
from app.models import Run, RunKind, RunStatus, RunTrigger
from app.services.runs import (
    RunAlreadyActive,
    claim_next_run,
    enqueue_run,
    enqueue_scheduled_runs,
    fail_interrupted_runs,
)
from tests.factories import create_competitor, create_run


async def test_claim_next_run_picks_oldest_queued(workspace):
    first = await create_run(workspace)
    await create_run(workspace)
    async with SessionLocal() as session:
        assert await claim_next_run(session) == first.id


async def test_claim_next_run_marks_run_running(workspace):
    run = await create_run(workspace)
    async with SessionLocal() as session:
        await claim_next_run(session)
        assert (await session.get(Run, run.id)).status == RunStatus.RUNNING


async def test_claim_next_run_returns_none_when_queue_empty(workspace):
    await create_run(workspace, RunStatus.PUBLISHED)
    async with SessionLocal() as session:
        assert await claim_next_run(session) is None


async def test_fail_interrupted_runs_fails_running_runs(workspace):
    run = await create_run(workspace, RunStatus.RUNNING)
    async with SessionLocal() as session:
        await fail_interrupted_runs(session)
        assert (await session.get(Run, run.id)).status == RunStatus.FAILED


async def test_enqueue_scheduled_runs_marks_trigger_scheduled(workspace):
    async with SessionLocal() as session:
        [run] = await enqueue_scheduled_runs(session)
    assert run.trigger == RunTrigger.SCHEDULED


async def test_enqueue_scheduled_runs_skips_workspace_with_active_check(workspace):
    await create_run(workspace)
    async with SessionLocal() as session:
        assert await enqueue_scheduled_runs(session) == []


async def test_enqueue_run_rejects_same_kind_while_active(workspace):
    await create_run(workspace, kind=RunKind.COMPANY_DISCOVERY)
    async with SessionLocal() as session:
        with pytest.raises(RunAlreadyActive):
            await enqueue_run(session, workspace.id, RunKind.COMPANY_DISCOVERY)


async def test_enqueue_run_allows_other_kind_while_active(workspace):
    await create_run(workspace)
    async with SessionLocal() as session:
        run = await enqueue_run(session, workspace.id, RunKind.COMPANY_DISCOVERY)
    assert run.status == RunStatus.QUEUED


async def test_enqueue_run_allows_page_discovery_for_another_competitor(workspace):
    first = await create_competitor(workspace, name="Acme")
    second = await create_competitor(workspace, name="Globex")
    await create_run(workspace, kind=RunKind.PAGE_DISCOVERY, competitor_id=first.id)
    async with SessionLocal() as session:
        run = await enqueue_run(
            session, workspace.id, RunKind.PAGE_DISCOVERY, competitor_id=second.id
        )
    assert run.competitor_id == second.id
