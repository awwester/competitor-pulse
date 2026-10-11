"""Domain errors raised by services. The API maps them to HTTP statuses (`app.main`) and the
MCP server to tool errors (`app.mcp_server`), so both enforce the same rules."""

from app.config import settings


class ServiceError(Exception):
    pass


class NotFound(ServiceError):
    pass


class Conflict(ServiceError):
    pass


class ReadOnly(ServiceError):
    pass


def ensure_writable() -> None:
    if settings.demo_mode:
        raise ReadOnly("This is a read-only demo.")
