"""MCP server for outside agents (Claude Code, Claude Desktop), mounted on the API at /mcp."""

from app.mcp_server import tools  # noqa: F401  (registers the tools)
from app.mcp_server.server import mcp

__all__ = ["mcp"]
