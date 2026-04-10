from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
    )


class DeleteResponse(ApiModel):
    id: UUID
    deleted: bool = True
    deleted_at: datetime


class CursorPage(ApiModel):
    next_cursor: str | None = None


JsonDict = dict[str, Any]
