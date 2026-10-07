from app.db import SessionLocal
from app.models import Run, RunStatus, RunTrigger
from app.services.runs import claim_next_run, enqueue_scheduled_runs, fail_interrupted_runs
from tests.factories import create_run


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
