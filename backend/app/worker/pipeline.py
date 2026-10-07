"""Executes one claimed run by handing it to the job for its kind."""

import logging
import uuid
from collections.abc import Awaitable, Callable

from app.db import SessionLocal
from app.models import Run, RunKind, RunStatus, Workspace
from app.services.run_log import RunLog
from app.services.runs import finish_run
from app.worker.check import execute_check
from app.worker.discovery import execute_company_discovery, execute_page_discovery

logger = logging.getLogger(__name__)

Job = Callable[[Run, Workspace, RunLog], Awaitable[None]]

JOBS: dict[RunKind, Job] = {
    RunKind.CHECK: execute_check,
    RunKind.COMPANY_DISCOVERY: execute_company_discovery,
    RunKind.PAGE_DISCOVERY: execute_page_discovery,
}


async def execute_run(run_id: uuid.UUID) -> None:
    log = await RunLog.for_run(run_id)
    async with SessionLocal() as session:
        run = await session.get(Run, run_id)
        workspace = await session.get(Workspace, run.workspace_id)

    try:
        await JOBS[run.kind](run, workspace, log)
    except Exception as exc:
        logger.exception("Run %s failed", run_id)
        await log.error(f"{type(exc).__name__}: {exc}")
        await finish_run(run_id, status=RunStatus.FAILED, error=str(exc))
