"""Helpers for in-process MCP tool results. Tools signal bad input with is_error, never raise."""

import json
import uuid
from typing import Any

ToolResult = dict[str, Any]


def text(value: str | dict | list) -> ToolResult:
    body = value if isinstance(value, str) else json.dumps(value, indent=2, default=str)
    return {"content": [{"type": "text", "text": body}]}


def error(message: str) -> ToolResult:
    return {"content": [{"type": "text", "text": message}], "is_error": True}


def parse_uuid(value: Any) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None
