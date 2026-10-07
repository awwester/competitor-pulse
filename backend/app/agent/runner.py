"""Shared Agent SDK loop: every agent here is a system prompt plus in-process MCP tools whose
trace streams into the run's RunLog."""

import tempfile
from dataclasses import dataclass
from typing import Any

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    SdkMcpTool,
    create_sdk_mcp_server,
    query,
)

from app.agent.tracing import SERVER_NAME, Usage, message_to_events, usage_from_result
from app.config import settings
from app.services.run_log import RunLog


@dataclass(frozen=True)
class AgentOutcome:
    usage: Usage
    error: str | None


def build_options(
    system_prompt: str, tools: list[SdkMcpTool[Any]], builtin_tools: list[str], cwd: str
) -> ClaudeAgentOptions:
    server = create_sdk_mcp_server(name=SERVER_NAME, tools=tools)
    tool_names = [f"mcp__{SERVER_NAME}__{t.name}" for t in tools]
    return ClaudeAgentOptions(
        model=settings.agent_model,
        effort=settings.agent_effort,
        thinking={"type": "adaptive", "display": "summarized"},
        system_prompt=system_prompt,
        mcp_servers={SERVER_NAME: server},
        # Built-in Claude Code tools the agent may use. Everything else (Bash, file editing,
        # etc.) is not loaded at all.
        tools=builtin_tools,
        allowed_tools=[*builtin_tools, *tool_names],
        # Anything not explicitly allowed is denied rather than prompting a human.
        permission_mode="dontAsk",
        max_turns=settings.agent_max_turns,
        max_budget_usd=settings.agent_max_budget_usd,
        # Isolate from any Claude Code settings/CLAUDE.md on the host.
        setting_sources=[],
        cwd=cwd,
    )


async def run_agent(
    *,
    system_prompt: str,
    task_prompt: str,
    tools: list[SdkMcpTool[Any]],
    builtin_tools: list[str],
    log: RunLog,
) -> AgentOutcome:
    """Run one agent to completion, streaming its trace into RunLog."""
    usage = Usage()
    error: str | None = None
    with tempfile.TemporaryDirectory(prefix="pulse-") as cwd:
        options = build_options(system_prompt, tools, builtin_tools, cwd)
        async for message in query(prompt=task_prompt, options=options):
            for event in message_to_events(message):
                await log.add(event.kind, event.payload)
            if isinstance(message, ResultMessage):
                usage = usage_from_result(message)
                if message.is_error:
                    error = "; ".join(message.errors or []) or f"Agent stopped: {message.subtype}"
    return AgentOutcome(usage=usage, error=error)
