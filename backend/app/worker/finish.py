import uuid
from typing import Any

from app.agent.runner import AgentOutcome
from app.models import RunStatus
from app.services.run_log import RunLog
from app.services.runs import finish_run


async def finish_agent_run(
    run_id: uuid.UUID,
    outcome: AgentOutcome,
    log: RunLog,
    *,
    missing: str | None,
    status: RunStatus,
    phase: tuple[str, str],
    **fields: Any,
) -> None:
    """Finish a run after its agent stops: failed on an agent error or missing output
    (`missing` says what's missing), otherwise `status`. Usage is recorded either way."""
    usage = vars(outcome.usage)
    if error := outcome.error or missing:
        await log.error(error)
        await finish_run(run_id, status=RunStatus.FAILED, error=error, **usage, **fields)
        return
    await log.phase(*phase)
    await finish_run(run_id, status=status, **usage, **fields)
