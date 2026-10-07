import tempfile
import uuid
from dataclasses import dataclass

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from app.agent.prompts import build_system_prompt, build_task_prompt
from app.agent.tools import SERVER_NAME, build_server
from app.agent.tracing import Usage, message_to_events, usage_from_result
from app.config import settings
from app.models import Workspace
from app.services.run_log import RunLog

# Built-in Claude Code tools the analyst may use for outside context. Everything else
# (Bash, file editing, etc.) is not loaded at all.
BUILTIN_TOOLS = ["WebSearch", "WebFetch"]


@dataclass(frozen=True)
class AnalysisOutcome:
    usage: Usage
    error: str | None


def build_options(workspace: Workspace, run_id: uuid.UUID, cwd: str) -> ClaudeAgentOptions:
    server, tool_names = build_server(run_id)
    return ClaudeAgentOptions(
        model=settings.agent_model,
        effort=settings.agent_effort,
        thinking={"type": "adaptive", "display": "summarized"},
        system_prompt=build_system_prompt(workspace),
        mcp_servers={SERVER_NAME: server},
        tools=BUILTIN_TOOLS,
        allowed_tools=[*BUILTIN_TOOLS, *tool_names],
        # Anything not explicitly allowed is denied rather than prompting a human.
        permission_mode="dontAsk",
        max_turns=settings.agent_max_turns,
        max_budget_usd=settings.agent_max_budget_usd,
        # Isolate from any Claude Code settings/CLAUDE.md on the host.
        setting_sources=[],
        cwd=cwd,
    )


async def analyze_run(
    workspace: Workspace, run_id: uuid.UUID, pages_changed: int, log: RunLog
) -> AnalysisOutcome:
    """Run the analyst agent over this run's changed pages, streaming its trace into RunLog."""
    usage = Usage()
    error: str | None = None
    with tempfile.TemporaryDirectory(prefix="pulse-") as cwd:
        options = build_options(workspace, run_id, cwd)
        async for message in query(prompt=build_task_prompt(pages_changed), options=options):
            for event in message_to_events(message):
                await log.add(event.kind, event.payload)
            if isinstance(message, ResultMessage):
                usage = usage_from_result(message)
                if message.is_error:
                    error = "; ".join(message.errors or []) or f"Agent stopped: {message.subtype}"
    return AnalysisOutcome(usage=usage, error=error)
