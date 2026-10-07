"""Translate Agent SDK messages into persisted trace events and usage totals."""

import json
from dataclasses import dataclass
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    Message,
    ResultMessage,
    ServerToolResultBlock,
    ServerToolUseBlock,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from app.agent.tools import SERVER_NAME
from app.models import RunEventKind
from app.services.diffing import truncate

MAX_RESULT_CHARS = 4_000
_MCP_PREFIX = f"mcp__{SERVER_NAME}__"


@dataclass(frozen=True)
class TraceEvent:
    kind: RunEventKind
    payload: dict[str, Any]


@dataclass(frozen=True)
class Usage:
    num_turns: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    cost_usd: float = 0.0


def _tool_name(name: str) -> str:
    return name.removeprefix(_MCP_PREFIX)


def _result_text(content: str | list[dict[str, Any]] | dict[str, Any] | None) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = [part.get("text", "") for part in content if part.get("type") == "text"]
        if texts:
            return "\n".join(texts)
    return json.dumps(content, default=str)


def _tool_call(block: ToolUseBlock | ServerToolUseBlock) -> TraceEvent:
    return TraceEvent(
        RunEventKind.TOOL_CALL,
        {"toolUseId": block.id, "name": _tool_name(block.name), "input": block.input},
    )


def _tool_result(tool_use_id: str, content: Any, is_error: bool | None) -> TraceEvent:
    return TraceEvent(
        RunEventKind.TOOL_RESULT,
        {
            "toolUseId": tool_use_id,
            "content": truncate(_result_text(content), MAX_RESULT_CHARS),
            "isError": bool(is_error),
        },
    )


def _block_event(block: Any) -> TraceEvent | None:
    match block:
        case TextBlock(text=text) if text.strip():
            return TraceEvent(RunEventKind.TEXT, {"text": text})
        case ThinkingBlock(thinking=thinking) if thinking.strip():
            return TraceEvent(RunEventKind.THINKING, {"text": thinking})
        case ToolUseBlock() | ServerToolUseBlock():
            return _tool_call(block)
        case ToolResultBlock(tool_use_id=tid, content=content, is_error=is_error):
            return _tool_result(tid, content, is_error)
        case ServerToolResultBlock(tool_use_id=tid, content=content):
            return _tool_result(tid, content, False)
    return None


def message_to_events(message: Message) -> list[TraceEvent]:
    match message:
        case AssistantMessage(content=blocks) | UserMessage(content=list() as blocks):
            return [event for block in blocks if (event := _block_event(block))]
        case ResultMessage():
            return [
                TraceEvent(
                    RunEventKind.RESULT,
                    {
                        "subtype": message.subtype,
                        "isError": message.is_error,
                        "numTurns": message.num_turns,
                        "durationMs": message.duration_ms,
                        "costUsd": message.total_cost_usd or 0.0,
                        "errors": message.errors or [],
                    },
                )
            ]
    return []


def usage_from_result(message: ResultMessage) -> Usage:
    usage = message.usage or {}
    return Usage(
        num_turns=message.num_turns,
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        cache_read_tokens=usage.get("cache_read_input_tokens", 0),
        cache_write_tokens=usage.get("cache_creation_input_tokens", 0),
        cost_usd=message.total_cost_usd or 0.0,
    )
