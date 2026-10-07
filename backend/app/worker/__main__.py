"""Worker process: runs scheduled checks and executes queued runs one at a time.

The queue is the runs table itself (SELECT … FOR UPDATE SKIP LOCKED), so no Redis or broker
is needed and additional workers can be started safely.
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.db import SessionLocal
from app.services.runs import claim_next_run, enqueue_scheduled_runs, fail_interrupted_runs
from app.worker.pipeline import execute_run

logger = logging.getLogger("worker")


async def enqueue_scheduled() -> None:
    async with SessionLocal() as session:
        runs = await enqueue_scheduled_runs(session)
    logger.info("Scheduled %d runs", len(runs))


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    async with SessionLocal() as session:
        if interrupted := await fail_interrupted_runs(session):
            logger.warning("Marked %d interrupted runs as failed", interrupted)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(enqueue_scheduled, CronTrigger.from_crontab(settings.schedule_cron))
    scheduler.start()
    logger.info("Worker started; schedule '%s'", settings.schedule_cron)

    while True:
        async with SessionLocal() as session:
            run_id = await claim_next_run(session)
        if run_id is None:
            await asyncio.sleep(settings.worker_poll_seconds)
            continue
        logger.info("Executing run %s", run_id)
        await execute_run(run_id)
        logger.info("Finished run %s", run_id)


if __name__ == "__main__":
    asyncio.run(main())
