from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from app.agent.tracing import message_to_events, usage_from_result
from app.models import RunEventKind


def result_message(**overrides) -> ResultMessage:
    fields = {
        "subtype": "success",
        "duration_ms": 1200,
        "duration_api_ms": 1000,
        "is_error": False,
        "num_turns": 7,
        "session_id": "s1",
        "total_cost_usd": 0.31,
        "usage": {"input_tokens": 100, "output_tokens": 50, "cache_read_input_tokens": 900},
        **overrides,
    }
    return ResultMessage(**fields)


def test_assistant_text_and_tool_use_become_events_in_order():
    message = AssistantMessage(
        content=[
            TextBlock(text="Checking the diff."),
            ToolUseBlock(id="t1", name="mcp__pulse__get_page_diff", input={"tracked_page_id": "x"}),
        ],
        model="claude-opus-5-5",
    )
    assert [e.kind for e in message_to_events(message)] == [
        RunEventKind.TEXT,
        RunEventKind.TOOL_CALL,
    ]


def test_tool_call_name_drops_mcp_prefix():
    message = AssistantMessage(
        content=[ToolUseBlock(id="t1", name="mcp__pulse__record_finding", input={})],
        model="claude-opus-5-5",
    )
    assert message_to_events(message)[0].payload["name"] == "record_finding"


def test_empty_text_blocks_are_skipped():
    message = AssistantMessage(content=[TextBlock(text="  ")], model="claude-opus-5-5")
    assert message_to_events(message) == []


def test_tool_result_text_parts_are_joined():
    message = UserMessage(
        content=[
            ToolResultBlock(
                tool_use_id="t1",
                content=[{"type": "text", "text": "line 1"}, {"type": "text", "text": "line 2"}],
            )
        ]
    )
    assert message_to_events(message)[0].payload["content"] == "line 1\nline 2"


def test_result_message_becomes_result_event_with_cost():
    [event] = message_to_events(result_message())
    assert (event.kind, event.payload["costUsd"]) == (RunEventKind.RESULT, 0.31)


def test_usage_from_result_maps_cache_tokens():
    assert usage_from_result(result_message()).cache_read_tokens == 900
