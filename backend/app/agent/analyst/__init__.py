import uuid

from app.agent.analyst.prompts import build_system_prompt, build_task_prompt
from app.agent.analyst.tools import build_tools
from app.agent.runner import AgentOutcome, run_agent
from app.config import settings
from app.models import Workspace
from app.services.run_log import RunLog

# Outside context: confirming an announcement or press release behind a change. WebSearch runs
# on Anthropic's servers; WebFetch would run here and could reach any URL a page told it to.
BUILTIN_TOOLS = ["WebSearch"]


async def analyze_run(
    workspace: Workspace, run_id: uuid.UUID, pages_changed: int, log: RunLog
) -> AgentOutcome:
    """Run the analyst agent over this run's changed pages."""
    return await run_agent(
        model=settings.analyst_model,
        system_prompt=build_system_prompt(workspace),
        task_prompt=build_task_prompt(pages_changed),
        tools=build_tools(run_id),
        builtin_tools=BUILTIN_TOOLS,
        log=log,
    )
