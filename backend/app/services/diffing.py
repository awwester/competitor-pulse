import difflib
import hashlib
import re
from dataclasses import dataclass

_WHITESPACE = re.compile(r"[ \t ]+")


def normalize_text(text: str) -> str:
    """Collapse whitespace and blank lines so cosmetic reflows don't register as changes."""
    lines = (_WHITESPACE.sub(" ", line).strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass(frozen=True)
class DiffResult:
    text: str
    lines_added: int
    lines_removed: int


def diff_text(before: str, after: str, *, context: int = 2) -> DiffResult:
    lines = list(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile="previous",
            tofile="current",
            n=context,
            lineterm="",
        )
    )
    body = [line for line in lines if not line.startswith(("---", "+++"))]
    return DiffResult(
        text="\n".join(lines),
        lines_added=sum(1 for line in body if line.startswith("+")),
        lines_removed=sum(1 for line in body if line.startswith("-")),
    )


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}\n… [truncated {len(text) - limit} chars]"
