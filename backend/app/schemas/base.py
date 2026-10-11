import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Schema(BaseModel):
    """camelCase on the wire, snake_case in Python."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)


def _http_url(value: str) -> str:
    """Accepts a bare domain like `ledgerly.com` and assumes https."""
    value = value.strip()
    if not _SCHEME.match(value):
        value = f"https://{value}"
    if not value.startswith(("http://", "https://")):
        raise ValueError("must start with http:// or https://")
    return value


HttpUrl = Annotated[str, Field(max_length=1000), AfterValidator(_http_url)]
