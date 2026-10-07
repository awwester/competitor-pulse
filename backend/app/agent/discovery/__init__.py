import uuid

from app.agent.discovery.prompts import (
    COMPANY_SYSTEM_PROMPT,
    company_task_prompt,
    pages_system_prompt,
    pages_task_prompt,
)
from app.agent.discovery.tools import build_company_tools, build_page_tools
from app.agent.runner import AgentOutcome, run_agent
from app.config import settings
from app.models import Competitor, Workspace
from app.services.crawler import Crawler
from app.services.run_log import RunLog

# Pages are read with our own Playwright tool (renders JS, reaches the local demo sites);
# WebSearch finds competitors the company's own site doesn't name.
COMPANY_BUILTIN_TOOLS = ["WebSearch"]


async def discover_company(workspace: Workspace, run_id: uuid.UUID, log: RunLog) -> AgentOutcome:
    """Profile the company from its website and suggest competitors for review."""
    async with Crawler() as crawler:
        return await run_agent(
            system_prompt=COMPANY_SYSTEM_PROMPT,
            task_prompt=company_task_prompt(workspace),
            tools=build_company_tools(run_id, workspace.id, crawler),
            builtin_tools=COMPANY_BUILTIN_TOOLS,
            log=log,
        )


async def discover_pages(competitor: Competitor, log: RunLog) -> AgentOutcome:
    """Choose and start tracking the pages worth monitoring on one competitor's site."""
    async with Crawler() as crawler:
        return await run_agent(
            system_prompt=pages_system_prompt(settings.discovery_max_pages),
            task_prompt=pages_task_prompt(competitor),
            tools=build_page_tools(competitor.id, crawler),
            builtin_tools=[],
            log=log,
        )
